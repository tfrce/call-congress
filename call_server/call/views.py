import random
import pystache
import twilio.twiml

from flask import abort, Blueprint, request, url_for, current_app
from flask_jsonpify import jsonify
from twilio import TwilioRestException
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import csrf, db

from .models import Call
from ..campaign.models import Campaign, Target
from ..political_data.lookup import locate_targets

from .decorators import crossdomain

call = Blueprint('call', __name__, url_prefix='/call')
call_methods = ['GET', 'POST']
csrf.exempt(call)


def play_or_say(r, audio, **kwds):
    # take twilio response and play or say message from an AudioRecording
    # can use mustache templates to render keyword arguments

    if audio:
        if hasattr(audio, 'file_storage'):
            r.play(audio.file_url())
        elif hasattr(audio, 'text_to_speech'):
            msg = pystache.render(audio.text_to_speech, kwds)
            r.say(msg)
        else:
            msg = pystache.render(audio, kwds)
            r.say(msg)
    else:
        r.say('Error: no recording defined')
        current_app.logger.error('Missing audio recording')
        current_app.logger.error(kwds)


def parse_params(r):
    params = {
        'userPhone': r.values.get('userPhone'),
        'campaignId': r.values.get('campaignId', 0),
        'zipcode': r.values.get('zipcode', None),
        'targetIds': r.values.getlist('targetIds'),
    }

    # lookup campaign by ID
    campaign = Campaign.query.get(params['campaignId'])

    if not campaign:
        return None, None

    # get target id by zip code
    if params['zipcode']:
        params['targetIds'] = locate_targets(params['zipcode'])

    return params, campaign


def intro_zip_gather(params, campaign):
    resp = twilio.twiml.Response()

    if campaign.audio('msg_intro_location'):
        play_or_say(resp, campaign.audio('msg_intro_location'),
                    organization=current_app.config.get('INSTALLED_ORG', ''))
    else:
        play_or_say(resp, campaign.audio('msg_intro'))

    return zip_gather(resp, params, campaign)


def zip_gather(resp, params, campaign):
    with resp.gather(numDigits=5, method="POST",
                     action=url_for("call.zip_parse", **params)) as g:
        play_or_say(g, campaign.audio('msg_location'))

    return str(resp)


def make_calls(params, campaign):
    """
    Connect a user to a sequence of targets.
    Required params: campaignId, targetIds
    Optional params: zipcode,
    """
    resp = twilio.twiml.Response()

    n_targets = len(params['targetIds'])

    play_or_say(resp, campaign.audio('msg_call_block_intro'),
                n_targets=n_targets, many=n_targets > 1)

    resp.redirect(url_for('call.make_single', call_index=0, **params))

    return str(resp)


@call.route('/make_calls', methods=call_methods)
def _make_calls():
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    return make_calls(params, campaign)


@call.route('/create', methods=call_methods)
@crossdomain(origin='*')
def create():
    """
    Makes a phone call to a user.
    Required Params:
        userPhone
        campaignId
    Optional Params:
        zipcode
        targetIds
    """
    # parse the info needed to make the call
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    # initiate the call
    try:
        call = current_app.config['TWILIO_CLIENT'].calls.create(
            to=params['userPhone'],
            from_=random.choice([str(n.number) for n in campaign.phone_number_set]),
            url=url_for('call.connection', _external=True, **params),
            timeLimit=current_app.config['TWILIO_TIME_LIMIT'],
            timeout=current_app.config['TWILIO_TIMEOUT'],
            status_callback=url_for("call.complete_status", _external=True, **params))

        result = jsonify(message=call.status, debugMode=current_app.debug)
        result.status_code = 200 if call.status != 'failed' else 500
    except TwilioRestException, err:
        result = jsonify(message=err.msg)
        result.status_code = 200

    return result


@call.route('/connection', methods=call_methods)
@crossdomain(origin='*')
def connection():
    """
    Call handler to connect a user with the campaign target(s).
    Required Params:
        campaignId
    Optional Params:
        zipcode
        targetIds (if not present go to incoming_call flow and asked for zipcode)
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    if params['targetIds']:
        resp = twilio.twiml.Response()

        play_or_say(resp, campaign.audio('msg_intro'))

        action = url_for("call._make_calls", **params)

        with resp.gather(numDigits=1, method="POST", timeout=10,
                         action=action) as g:
            play_or_say(g, campaign.audio('msg_intro_confirm'))

            return str(resp)
    else:
        return intro_zip_gather(params, campaign)


@call.route('/incoming', methods=call_methods)
def incoming():
    """
    Handles incoming calls to the twilio numbers.
    Required Params: campaignId

    Each Twilio phone number needs to be configured to point to:
    server.org/incoming_call?campaignId=12345
    from twilio.com/user/account/phone-numbers/incoming
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    return intro_zip_gather(params, campaign)


@call.route("/zip_parse", methods=call_methods)
def zip_parse():
    """
    Handle a zip code entered by the user.
    Required Params: campaignId, Digits
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    zipcode = request.values.get('Digits', '')
    target_ids = locate_targets(zipcode)

    if current_app.debug:
        current_app.logger.debug('zipcode = {}'.format(zipcode))

    if not target_ids:
        resp = twilio.twiml.Response()
        play_or_say(resp, campaign.audio('msg_invalid_zip'))

        return zip_gather(resp, params, campaign)

    params['zipcode'] = zipcode
    params['targetIds'] = target_ids

    return make_calls(params, campaign)


@call.route('/make_single', methods=call_methods)
def make_single():
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    i = int(request.values.get('call_index', 0))
    params['call_index'] = i

    target_bioguide = params['targetIds'][i]
    current_target, cached = Target.get_uid_or_cache(target_bioguide, 'us:bioguide')
    if cached:
        # save Target to database
        db.session.add(current_target)
        db.session.commit()

    target_phone = str(current_target.number)
    full_name = current_target.full_name()

    resp = twilio.twiml.Response()

    play_or_say(resp, campaign.audio('msg_target_intro'), name=full_name)

    if current_app.debug:
        current_app.logger.debug('Call #{}, {} ({}) from {} in call.make_single()'.format(
            i, full_name, target_phone, params['userPhone']))

    resp.dial(target_phone, callerId=params['userPhone'],
              timeLimit=current_app.config['TWILIO_TIME_LIMIT'],
              timeout=current_app.config['TWILIO_TIMEOUT'], hangupOnStar=True,
              action=url_for('call.complete', **params))

    return str(resp)


@call.route('/complete', methods=call_methods)
def complete():
    params, campaign = parse_params(request)
    i = int(request.values.get('call_index', 0))

    if not params or not campaign:
        abort(404)

    current_target = Target.query.filter(Target.uid == params['targetIds'][i]).first()
    call_data = {
        'campaign_id': campaign.id,
        'target_id': current_target.id,
        'location': params['zipcode'],
        'call_id': request.values.get('CallSid', None),
        'status': request.values.get('DialCallStatus', 'unknown'),
        'duration': request.values.get('DialCallDuration', 0)
    }
    if current_app.config['LOG_PHONE_NUMBERS']:
        call_data['phone_number'] = params['userPhone']
        # user phone numbers are hashed by the init method
        # but some installations may not want to log at all

    try:
        db.session.add(Call(**call_data))
        db.session.commit()
    except SQLAlchemyError:
        current_app.logger.error('Failed to log call:', exc_info=True)

    resp = twilio.twiml.Response()

    i = int(request.values.get('call_index', 0))

    if i == len(params['targetIds']) - 1:
        # thank you for calling message
        play_or_say(resp, campaign.audio('msg_final_thanks'))
    else:
        # call the next target
        params['call_index'] = i + 1  # increment the call counter

        play_or_say(resp, campaign.audio('msg_between_calls'))

        resp.redirect(url_for('call.make_single', **params))

    return str(resp)


@call.route('/complete_status', methods=call_methods)
def complete_status():
    # async callback from twilio on call complete
    params, _ = parse_params(request)

    if not params:
        abort(404)

    return jsonify({
        'phoneNumber': request.values.get('To', ''),
        'callStatus': request.values.get('CallStatus', 'unknown'),
        'targetIds': params['targetIds'],
        'campaignId': params['campaignId']
    })
