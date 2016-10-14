import random
import pystache
import twilio.twiml
from sqlalchemy_utils.types.phone_number import PhoneNumber, phonenumbers

from flask import abort, Blueprint, request, url_for, current_app
from flask_jsonpify import jsonify
from twilio import TwilioRestException
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import csrf, db

from .models import Call, Session
from ..campaign.constants import ORDER_SHUFFLE, LOCATION_POSTAL, LOCATION_DISTRICT
from ..campaign.models import Campaign, Target
from ..political_data.lookup import locate_targets

from .decorators import crossdomain, abortJSON, stripANSI

call = Blueprint('call', __name__, url_prefix='/call')
call_methods = ['GET', 'POST']
csrf.exempt(call)
call.errorhandler(400)(abortJSON)


def play_or_say(r, audio, **kwds):
    """
    Take twilio response and play or say message from an AudioRecording
    Can use mustache templates to render keyword arguments
    """

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


def parse_params(r, inbound=False):
    """
    Rehydrate objects from the parameter list.
    Gets invoked before each Twilio call.
    Should not edit param values.
    """
    params = {
        'sessionId': r.values.get('sessionId', None),
        'campaignId': r.values.get('campaignId', None),
        'userPhone': r.values.get('userPhone', None),
        'userCountry': r.values.get('userCountry', 'US'),
        'userLocation': r.values.get('userLocation', None),
        'targetIds': r.values.getlist('targetIds'),
    }

    if (not params['userPhone']) and not inbound:
        abort(400, 'userPhone required')

    if not params['campaignId']:
        abort(400, 'campaignId required')

    # lookup campaign by ID
    campaign = Campaign.query.get(params['campaignId'])
    if not campaign:
        abort(400, 'invalid campaignId %(campaignId)s' % params)

    return params, campaign


def parse_target(key):
    """
    Split target key into (uid, prefix)

    >>> parse_target("us:bioguide_id:ASDF")
    ("ASDF", "us:bioguide_id")
    """
    try:
        pieces = key.split(':')
        uid = pieces[-1]
        prefix = ':'.join(pieces[0:-1])
    except ValueError:
        current_app.logger.error('got malformed target key: "%s"' % key)
        uid = key
        prefix = None
    return (uid, prefix)


def intro_wait_human(params, campaign):
    """
    Play intro message, and wait for key press to ensure we have a human on the line.
    Then, redirect to _make_calls.
    """
    resp = twilio.twiml.Response()

    play_or_say(resp, campaign.audio('msg_intro'))

    action = url_for("call._make_calls", **params)

    # wait for user keypress, in case we connected to voicemail
    # give up after 10 seconds
    with resp.gather(numDigits=1, method="POST", timeout=10,
                     action=action) as g:
        play_or_say(g, campaign.audio('msg_intro_confirm'))

        return str(resp)


def intro_location_gather(params, campaign):
    """
    If specified, play msg_intro_location audio. Otherwise, standard msg_intro.
    Then, return location_gather.
    """
    resp = twilio.twiml.Response()

    if campaign.audio('msg_intro_location'):
        play_or_say(resp, campaign.audio('msg_intro_location'),
                    organization=current_app.config.get('INSTALLED_ORG', ''))
    else:
        play_or_say(resp, campaign.audio('msg_intro'))

    return location_gather(resp, params, campaign)


def location_gather(resp, params, campaign):
    """
    Play msg_location, and wait for 5 digits from user.
    Then, redirect to location_parse
    """
    with resp.gather(numDigits=5, method="POST",
                     action=url_for("call.location_parse", **params)) as g:
        play_or_say(g, campaign.audio('msg_location'))

    return str(resp)


def make_calls(params, campaign):
    """
    Connect a user to a sequence of targets.
    Performs target lookup, shuffling, and limiting to maximum.
    Plays msg_call_block_intro, then redirects to make_single call.

    Required params: campaignId, targetIds
    """
    resp = twilio.twiml.Response()

    # check if campaign target_set specified
    if not params['targetIds'] and campaign.target_set:
        params['targetIds'] = [t.uid for t in campaign.target_set]
    else:
        # lookup targets for campaign type by segment, put in desired order
        params['targetIds'] = locate_targets(params['userLocation'], campaign=campaign)

    if not params['targetIds']:
        play_or_say(resp, campaign.audio('msg_invalid_location'), location=params['userLocation'])
        resp.hangup()

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
        abort(400)

    return make_calls(params, campaign)


@call.route('/create', methods=call_methods)
@crossdomain(origin='*')
def create():
    """
    Places a phone call to a user, given a country, phone number, and campaign.

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

    # find outgoing phone number in same country as user
    phone_numbers = campaign.phone_numbers(params['userCountry'])

    if not phone_numbers:
        msg = "no numbers available for campaign %(campaignId)s in %(userCountry)s" % params
        return abort(400, msg)

    # validate phonenumber for country
    try:
        parsed = PhoneNumber(params['userPhone'], params['userCountry'])
        userPhone = parsed.e164
    except phonenumbers.NumberParseException:
        current_app.logger.error('Unable to parse %(userPhone)s for %(userCountry)s' % params)
        # press onward, but we may not be able to actually dial
        userPhone = params['userPhone']

    # start call session for user
    try:
        from_number = random.choice(phone_numbers)

        call_session_data = {
            'campaign_id': campaign.id,
            'location': params['userLocation'],
            'from_number': from_number,
        }
        if current_app.config['LOG_PHONE_NUMBERS']:
            call_session_data['phone_number'] = params['userPhone']
            # user phone numbers are hashed by the init method
            # but some installations may not want to log at all

        call_session = Session(**call_session_data)
        db.session.add(call_session)
        db.session.commit()

        params['sessionId'] = call_session.id

        # initiate outbound call
        call = current_app.config['TWILIO_CLIENT'].calls.create(
            to=userPhone,
            from_=from_number,
            url=url_for('call.connection', _external=True, **params),
            timeLimit=current_app.config['TWILIO_TIME_LIMIT'],
            timeout=current_app.config['TWILIO_TIMEOUT'],
            status_callback=url_for("call.complete_status", _external=True, **params))

        if campaign.embed:
            script = campaign.embed.get('script')
        else:
            script = ''
        result = jsonify(campaign=campaign.status, call=call.status, script=script)
        result.status_code = 200 if call.status != 'failed' else 500
    except TwilioRestException, err:
        twilio_error = stripANSI(err.msg)
        abort(400, twilio_error)

    return result


@call.route('/connection', methods=call_methods)
@crossdomain(origin='*')
def connection():
    """
    Call handler to connect a user with the targets for a given campaign.
    Redirects to intro_location_gather if campaign requires, or intro_wait_human if not.

    Required Params:
        campaignId
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        return abortJSON(404)

    if campaign.locate_by in [LOCATION_POSTAL, LOCATION_DISTRICT] and not params['userLocation']:
        return intro_location_gather(params, campaign)
    else:
        return intro_wait_human(params, campaign)


@call.route('/incoming', methods=call_methods)
def incoming():
    """
    Handles incoming calls to the twilio numbers.
    Required Params: campaignId

    Each Twilio phone number needs to be configured to point to:
    server.org/call/incoming?campaignId=12345
    from twilio.com/user/account/phone-numbers/incoming
    """
    params, campaign = parse_params(request, inbound=True)

    if not params or not campaign:
        abort(400)

    # pull user phone from Twilio incoming request
    params['userPhone'] = request.values.get('From')

    if campaign.locate_by in [LOCATION_POSTAL, LOCATION_DISTRICT]:
        return intro_location_gather(params, campaign)
    else:
        return intro_wait_human(params, campaign)


@call.route("/location_parse", methods=call_methods)
def location_parse():
    """
    Handle location entered by the user.
    Required Params: campaignId, Digits
    """
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(400)

    location = request.values.get('Digits', '')

    # Override location method so locate_targets knows we're passing a zip
    # This allows call-ins to be made for campaigns which otherwise use district locate_by
    campaign.locate_by = LOCATION_POSTAL
    target_ids = locate_targets(location, campaign)

    if current_app.debug:
        current_app.logger.debug('entered = {}'.format(location))

    if not target_ids:
        resp = twilio.twiml.Response()
        play_or_say(resp, campaign.audio('msg_unparsed_location'))

        return location_gather(resp, params, campaign)

    params['userLocation'] = location
    params['targetIds'] = target_ids

    return make_calls(params, campaign)


@call.route('/make_single', methods=call_methods)
def make_single():
    params, campaign = parse_params(request)

    if not params or not campaign:
        abort(400)

    i = int(request.values.get('call_index', 0))
    params['call_index'] = i

    (uid, prefix) = parse_target(params['targetIds'][i])
    (current_target, cached) = Target.get_uid_or_cache(uid, prefix)
    if cached:
        # save Target to database
        db.session.add(current_target)
        db.session.commit()

    resp = twilio.twiml.Response()

    if not current_target.number:
        play_or_say(resp, campaign.audio('msg_invalid_location'))
        return str(resp)

    target_phone = current_target.number.e164  # use full E164 syntax here
    play_or_say(resp, campaign.audio('msg_target_intro'),
        title=current_target.title, name=current_target.name)

    if current_app.debug:
        current_app.logger.debug('Call #{}, {} ({}) from {} in call.make_single()'.format(
            i, current_target.name, target_phone, params['userPhone']))

    userPhone = PhoneNumber(params['userPhone'], params['userCountry'])

    resp.dial(target_phone, callerId=userPhone.e164,
              timeLimit=current_app.config['TWILIO_TIME_LIMIT'],
              timeout=current_app.config['TWILIO_TIMEOUT'], hangupOnStar=True,
              action=url_for('call.complete', **params))

    return str(resp)


@call.route('/complete', methods=call_methods)
def complete():
    params, campaign = parse_params(request)
    i = int(request.values.get('call_index', 0))

    if not params or not campaign:
        abort(400)

    (uid, prefix) = parse_target(params['targetIds'][i])
    (current_target, cached) = Target.get_uid_or_cache(uid, prefix)
    call_data = {
        'session_id': params['sessionId'],
        'campaign_id': campaign.id,
        'target_id': current_target.id,
        'call_id': request.values.get('CallSid', None),
        'status': request.values.get('DialCallStatus', 'unknown'),
        'duration': request.values.get('DialCallDuration', 0)
    }

    try:
        db.session.add(Call(**call_data))
        db.session.commit()
    except SQLAlchemyError:
        current_app.logger.error('Failed to log call:', exc_info=True)

    resp = twilio.twiml.Response()

    if call_data['status'] == 'busy':
        play_or_say(resp, campaign.audio('msg_target_busy'),
            title=current_target.title, name=current_target.name)

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
        abort(400)

    # update call_session with complete status
    call_session = Session.query.get(request.values.get('sessionId'))
    call_session.status = request.values.get('CallStatus', 'unknown')
    call_session.duration = request.values.get('CallDuration', None)
    db.session.add(call_session)
    db.session.commit()

    return jsonify({
        'phoneNumber': request.values.get('To', ''),
        'callStatus': call_session.status,
        'targetIds': params['targetIds'],
        'campaignId': params['campaignId']
    })
