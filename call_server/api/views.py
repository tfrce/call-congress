import json
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
import dateutil

import twilio.twiml
from flask import Blueprint, Response, render_template, abort, request, jsonify

from sqlalchemy.sql import func, extract, distinct

from decorators import api_key_or_auth_required, restless_api_auth
from ..utils import median
from ..call.decorators import crossdomain

from constants import API_TIMESPANS

from ..extensions import csrf, rest, db
from ..campaign.models import Campaign, Target, AudioRecording
from ..call.models import Call, Session
from ..call.constants import TWILIO_CALL_STATUS


api = Blueprint('api', __name__, url_prefix='/api')
csrf.exempt(api)


restless_preprocessors = {'GET_SINGLE':   [restless_api_auth],
                          'GET_MANY':     [restless_api_auth],
                          'PATCH_SINGLE': [restless_api_auth],
                          'PATCH_MANY':   [restless_api_auth],
                          'PUT_SINGLE':   [restless_api_auth],
                          'PUT_MANY':     [restless_api_auth],
                          'POST':         [restless_api_auth],
                          'DELETE':       [restless_api_auth]}


def configure_restless(app):
    rest.create_api(Call, collection_name='call', methods=['GET'],
                    include_columns=['id', 'timestamp', 'campaign_id', 'target_id',
                                    'call_id', 'status', 'duration'],
                    include_methods=['target_display'])
    rest.create_api(Campaign, collection_name='campaign', methods=['GET'],
                    include_columns=['id', 'name', 'campaign_type', 'campaign_state', 'campaign_subtype',
                                     'target_ordering', 'allow_call_in', 'call_maximum', 'embed'],
                    include_methods=['phone_numbers', 'targets', 'status', 'audio_msgs', 'required_fields'])
    rest.create_api(Target, collection_name='target', methods=['GET'],
                    include_columns=['id', 'uid', 'name', 'title'],
                    include_methods=['phone_number'])
    rest.create_api(AudioRecording, collection_name='audiorecording', methods=['GET'],
                    include_columns=['id', 'key', 'version', 'description',
                                     'text_to_speech', 'hidden'],
                    include_methods=['file_url', 'campaign_names', 'campaign_ids',
                                     'selected_campaign_names', 'selected_campaign_ids'])


# non CRUD-routes

# simple call count
# NOT PROTECTED
@api.route('/campaign/<int:campaign_id>/count.json', methods=['GET'])
def campaign_count(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()

    # number of calls completed in campaign
    calls_completed = db.session.query(
        Call.timestamp, Call.id
    ).filter_by(
        campaign_id=campaign.id,
        status='completed'
    ).all()

    return jsonify({'completed', calls_completed})


# more detailed campaign statistics
# protect with decorator
@api.route('/campaign/<int:campaign_id>/stats.json', methods=['GET'])
@api_key_or_auth_required
def campaign_stats(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()

    # number of sessions started in campaign
    sessions_started = db.session.query(
        func.count(Session.id)
    ).filter_by(
        campaign_id=campaign.id
    ).scalar()

    # number of sessions completed in campaign
    sessions_completed = db.session.query(
        func.count(Session.id)
    ).filter_by(
        campaign_id=campaign.id,
        status='completed'
    ).scalar()

    # number of calls completed in campaign
    calls_completed = db.session.query(
        Call.timestamp, Call.id
    ).filter_by(
        campaign_id=campaign.id,
        status='completed'
    ).all()

    # list of completed calls per session in campaign
    calls_session_grouped = db.session.query(
        func.count(Call.id)
    ).filter(
        Call.campaign_id == campaign.id,
        Call.status == 'completed',
        Call.session_id != None
    ).group_by(
        Call.session_id
    ).all()
    calls_session_list = [int(n[0]) for n in calls_session_grouped]
    calls_per_session = median(calls_session_list)

    data = {
        'id': campaign.id,
        'name': campaign.name,
        'sessions_completed': sessions_completed,
        'sessions_started': sessions_started,
        'calls_per_session': calls_per_session,
    }

    if calls_completed:
        data.update({
            'date_start': datetime.strftime(calls_completed[0][0], '%Y-%m-%d'),
            'date_end': datetime.strftime(calls_completed[-1][0] + timedelta(days=1), '%Y-%m-%d'),
            'calls_completed': len(calls_completed)
        })

    return jsonify(data)


# calls grouped by timespan
@api.route('/campaign/<int:campaign_id>/date_calls.json', methods=['GET'])
@api_key_or_auth_required
def campaign_date_calls(campaign_id):
    start = request.values.get('start')
    end = request.values.get('end')
    timespan = request.values.get('timespan', 'day')

    if timespan not in API_TIMESPANS.keys():
        abort(400, 'timespan should be one of %s' % ','.join(API_TIMESPANS))
    else:
        timespan_strf = API_TIMESPANS[timespan]

    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    timespan_extract = extract(timespan, Call.timestamp).label(timespan)

    query = (
        db.session.query(
            func.min(Call.timestamp.label('date')),
            timespan_extract,
            Call.status,
            func.count(distinct(Call.id)).label('calls_count')
        )
        .filter(Call.campaign_id == int(campaign.id))
        .group_by(timespan_extract)
        .order_by(timespan)
        .group_by(Call.status)
    )

    if start:
        try:
            startDate = dateutil.parser.parse(start)
        except ValueError:
            abort(400, 'start should be in isostring format')
        query = query.filter(Call.timestamp >= startDate)

    if end:
        try:
            endDate = dateutil.parser.parse(end)
            if endDate < startDate:
                abort(400, 'end should be after start')
            if endDate == startDate:
                endDate = startDate + timedelta(days=1)
        except ValueError:
            abort(400, 'end should be in isostring format')
        query = query.filter(Call.timestamp <= endDate)

    dates = defaultdict(dict)

    for (date, timespan, call_status, count) in query.all():
        # combine status values by date
        for status in TWILIO_CALL_STATUS:
            if call_status == status:
                date_string = date.strftime(timespan_strf)
                dates[date_string][status] = count
    sorted_dates = OrderedDict(sorted(dates.items()))
    return Response(json.dumps(sorted_dates), mimetype='application/json')


# calls made by target
@api.route('/campaign/<int:campaign_id>/target_calls.json', methods=['GET'])
@api_key_or_auth_required
def campaign_target_calls(campaign_id):
    start = request.values.get('start')
    end = request.values.get('end')

    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()

    query_calls = (
        db.session.query(
            Call.target_id,
            Call.status,
            func.count(distinct(Call.id)).label('calls_count')
        )
        .filter(Call.campaign_id == int(campaign.id))
        .group_by(Call.target_id)
        .group_by(Call.status)
    )

    if start:
        try:
            startDate = dateutil.parser.parse(start)
        except ValueError:
            abort(400, 'start should be in isostring format')
        query_calls = query_calls.filter(Call.timestamp >= startDate)

    if end:
        try:
            endDate = dateutil.parser.parse(end)
            if endDate < startDate:
                abort(400, 'end should be after start')
            if endDate == startDate:
                endDate = startDate + timedelta(days=1)
        except ValueError:
            abort(400, 'end should be in isostring format')
        query_calls = query_calls.filter(Call.timestamp <= endDate)

    # join with targets for name
    subquery = query_calls.subquery('query_calls')
    query_targets = (
        db.session.query(
            Target.name,
            subquery.c.status,
            subquery.c.calls_count
        )
        .join(subquery, subquery.c.target_id == Target.id)
    )

    # in case some calls don't get matched directly to targets
    # they are filtered out by join, so hold on to them
    calls_wo_targets = query_calls.filter(Call.target_id == None)

    targets = defaultdict(dict)

    for status in TWILIO_CALL_STATUS:
        # combine calls status for each target
        for (target_name, call_status, count) in query_targets.all():
            if call_status == status:
                targets[target_name][call_status] = targets.get(target_name, {}).get(call_status, 0) + count

        for (target_name, call_status, count) in calls_wo_targets.all():
            if call_status == status:
                targets['Unknown'][call_status] = targets.get('Unknown', {}).get(call_status, 0) + count
    return Response(json.dumps(targets), mimetype='application/json')


# embed campaign routes, should be public
# js must be crossdomain
@api.route('/campaign/<int:campaign_id>/embed.js', methods=['GET'])
@crossdomain(origin='*')
def campaign_embed_js(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    return render_template('api/embed.js', campaign=campaign, mimetype='text/javascript')


@api.route('/campaign/<int:campaign_id>/CallPowerForm.js', methods=['GET'])
@crossdomain(origin='*')
def campaign_form_js(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    return render_template('api/CallPowerForm.js', campaign=campaign, mimetype='text/javascript')


@api.route('/campaign/<int:campaign_id>/embed_iframe.html', methods=['GET'])
def campaign_embed_iframe(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    return render_template('api/embed_iframe.html', campaign=campaign)


@api.route('/campaign/<int:campaign_id>/embed_code.html', methods=['GET'])
@api_key_or_auth_required
def campaign_embed_code(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    # kludge new params into campaign object to render
    temp_params = {
        'type': request.values.get('embed_type'),
        'form_sel': request.values.get('embed_form_sel', None),
        'phone_sel': request.values.get('embed_phone_sel', None),
        'location_sel': request.values.get('embed_location_sel', None),
        'custom_css': request.values.get('embed_custom_css'),
        'custom_js': request.values.get('embed_custom_js'),
        'script_display': request.values.get('embed_script_display'),
    }
    if type(campaign.embed) == dict():
        campaign.embed.update(temp_params)
    else:
        campaign.embed = temp_params
    # don't save
    return render_template('api/embed_code.html', campaign=campaign)


# route for twilio to get twiml response
# must be publicly accessible to post
@api.route('/twilio/text-to-speech', methods=['POST'])
def twilio_say():
    resp = twilio.twiml.Response()
    resp.say(request.values.get('text'))
    resp.hangup()
    return str(resp)
