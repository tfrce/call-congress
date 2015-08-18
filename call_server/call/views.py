import random
import pystache
import twilio.twiml

from flask import abort, Blueprint, request, url_for, current_app
from flask_jsonpify import jsonify
from twilio import TwilioRestException
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import csrf, db

from .models import Call
from ..campaign.constants import ORDER_SHUFFLE
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
        if (hasattr(audio, 'text_to_speech') and not (audio.text_to_speech == '')):
            msg = pystache.render(audio.text_to_speech, kwds)
            r.say(msg)
        elif (hasattr(audio, 'file_storage') and (audio.file_storage.fp is not None)):
            r.play(audio.file_url())
        elif type(audio) == str:
            try:
                msg = pystache.render(audio, kwds)
                r.say(msg)
            except Exception:
                current_app.logger.error('Unable to render pystache template %s' % audio)
                r.say(audio)
        else:
            current_app.logger.error('Unknown audio type %s' % type(audio))
    else:
        r.say('Error: no recording defined')
        current_app.logger.error('Missing audio recording')
        current_app.logger.error(kwds)


def parse_params(r):
    params = {
        'campaignId': r.values.get('campaignId', 0),
        'userPhone': r.values.get('userPhone', ''),
        'userCountry': r.values.get('userCountry', 'US'),
        'userLocation': r.values.get('userLocation', None),
        'targetIds': r.values.getlist('targetIds'),
    }

    # lookup campaign by ID
    campaign = Campaign.query.get(params['campaignId'])
    if not campaign:
        return None, None

    return params, campaign


def parse_target(key):
    try:
        pieces = key.split(':')
        uid = pieces[-1]
        prefix = ':'.join(pieces[0:-1])
    except ValueError:
        current_app.logger.error('got malformed target key: "%s"' % key)
        uid = key
        prefix = None
    return (uid, prefix)


def intro_location_gather(params, campaign):
    resp = twilio.twiml.Response()

    if campaign.audio('msg_intro_location'):
        play_or_say(resp, campaign.audio('msg_intro_location'),
                    organization=current_app.config.get('INSTALLED_ORG', ''))
    else:
        play_or_say(resp, campaign.audio('msg_intro'))

    return location_gather(resp, params, campaign)


def location_gather(resp, params, campaign):
    with resp.gather(numDigits=5, method="POST",
                     action=url_for("call.location_parse", **params)) as g:
        play_or_say(g, campaign.audio('msg_location'))

    return str(resp)


def make_calls(params, campaign):
    """
    Connect a user to a sequence of targets.
    Required params: campaignId, targetIds
    """
    resp = twilio.twiml.Response()

    # check if campaign target_set specified
    if not params['targetIds'] and campaign.target_set:
        params['targetIds'] = [t.uid for t in campaign.target_set]
    else:
        # lookup targets for campaign type by segment, put in desired order
        params['targetIds'] = locate_targets(params['userLocation'], campaign=campaign)

    if campaign.target_ordering == ORDER_SHUFFLE:
        # reshuffle for each caller
        random.shuffle(params['targetIds'])

    # limit calls to maximum number
    if campaign.call_maximum:
        params['targetIds'] = params['targetIds'][:campaign.call_maximum]

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
        userCountry (defaults to US)
        userLocation (zipcode)
        targetIds
    """
    # parse the info needed to make the call
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    # find outgoing phone number in same country as user
    phone_numbers = campaign.phone_numbers(params['userCountry'])

    if not phone_numbers:
        current_app.logger.error("no numbers available for campaign %(campaignId)d in %(userCountry)s" % params)
        abort(500)

    # initiate the call
    try:
        call = current_app.config['TWILIO_CLIENT'].calls.create(
            to=params['userPhone'],
            from_=random.choice(phone_numbers),
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
        userLocation (zipcode)
        targetIds (if not present go to incoming_call flow and prompt for zipcode)
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
        return intro_location_gather(params, campaign)


@call.route('/incoming', methods=call_methods)
def incoming():
    """
    Handles incoming calls to the twilio numbers.
    Required Params: campaignId

    Each Twilio phone number needs to be configured to point to:
    server.org/call/incoming?campaignId=12345
    from twilio.com/user/account/phone-numbers/incoming
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    return intro_location_gather(params, campaign)


@call.route("/location_parse", methods=call_methods)
def location_parse():
    """
    Handle location (usually zipcode) entered by the user.
    Required Params: campaignId, Digits
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    location = request.values.get('Digits', '')
    target_ids = locate_targets(location, campaign)

    if current_app.debug:
        current_app.logger.debug('entered = {}'.format(location))

    if not target_ids:
        resp = twilio.twiml.Response()
        play_or_say(resp, campaign.audio('msg_invalid_location'))

        return location_gather(resp, params, campaign)

    params['userLocation'] = location
    params['targetIds'] = target_ids

    return make_calls(params, campaign)


@call.route('/make_single', methods=call_methods)
def make_single():
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(404)

    i = int(request.values.get('call_index', 0))
    params['call_index'] = i

    (uid, prefix) = parse_target(params['targetIds'][i])
    (current_target, cached) = Target.get_uid_or_cache(uid, prefix)
    if cached:
        # save Target to database
        db.session.add(current_target)
        db.session.commit()

    target_phone = current_target.number.international  # use full E164 syntax here
    full_name = current_target.full_name()

    resp = twilio.twiml.Response()

    play_or_say(resp, campaign.audio('msg_target_intro'),
        title=current_target.title, name=full_name)

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

    (uid, prefix) = parse_target(params['targetIds'][i])
    (current_target, cached) = Target.get_uid_or_cache(uid, prefix)
    call_data = {
        'campaign_id': campaign.id,
        'target_id': current_target.id,
        'location': params['userLocation'],
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
