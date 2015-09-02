import json
from collections import OrderedDict
from datetime import datetime, timedelta
import dateutil

import twilio.twiml
from flask import Blueprint, Response, render_template, abort, request, jsonify

from sqlalchemy.sql import func, extract

from decorators import api_key_or_auth_required, restless_api_auth
from ..call.decorators import crossdomain

from constants import API_TIMESPANS

from ..extensions import csrf, rest, db
from ..campaign.models import Campaign, Target, AudioRecording
from ..call.models import Call


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
                                    'call_id', 'status', 'duration'])
    rest.create_api(Campaign, collection_name='campaign', methods=['GET'],
                    include_columns=['id', 'name', 'campaign_type', 'campaign_state', 'campaign_subtype',
                                     'target_ordering', 'allow_call_in', 'call_maximum'],
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
# protect with decorator
@api.route('/campaign/<int:campaign_id>/stats.json', methods=['GET'])
@api_key_or_auth_required
def campaign_stats(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    completed = db.session.query(
        func.count(Call.id)
    ).filter_by(
        campaign_id=campaign.id,
        status='completed'
    ).scalar()
    total_count = db.session.query(
        func.count(Call.id)
    ).filter_by(
        campaign_id=campaign.id
    ).scalar()

    return jsonify({
        'id': campaign.id,
        'name': campaign.name,
        'completed': completed,
        'total_count': total_count
    })


@api.route('/campaign/<int:campaign_id>/call_chart.json', methods=['GET'])
@api_key_or_auth_required
def campaign_call_chart(campaign_id):
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
            func.count(Call.id).label('calls_count')
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

    # create a separate series for each status value
    series = []

    STATUS_LIST = ('completed', 'canceled', 'failed')
    for status in STATUS_LIST:
        data = {}
        # combine status values by date
        for (date, timespan, call_status, count) in query.all():
            # entry like ('2015-08-10', u'canceled', 8)
            if call_status == status:
                date_string = date.strftime(timespan_strf)
                data[date_string] = count
        new_series = {'name': status.capitalize(),
                      'data': OrderedDict(sorted(data.items()))}
        series.append(new_series)
    return Response(json.dumps(series), mimetype='application/json')


# embed campaign routes, should be public
# js must be crossdomain
@api.route('/campaign/<int:campaign_id>/embed.js', methods=['GET'])
@crossdomain(origin='*')
def campaign_embed_js(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    return render_template('api/embed.js', campaign=campaign, mimetype='text/javascript')


@api.route('/campaign/<int:campaign_id>/embed_iframe.html', methods=['GET'])
def campaign_embed_iframe(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    return render_template('api/embed_iframe.html', campaign=campaign)


@api.route('/twilio/text-to-speech', methods=['POST'])
def twilio_say():
    resp = twilio.twiml.Response()
    resp.say(request.values.get('text'))
    resp.hangup()
    return str(resp)
