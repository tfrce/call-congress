import json
from collections import OrderedDict

from flask import Blueprint, Response, render_template
from sqlalchemy.sql import func

from decorators import api_key_or_auth_required, restless_api_auth
from ..call.decorators import crossdomain

from ..extensions import rest, db
from ..campaign.models import Campaign, Target, AudioRecording
from ..call.models import Call


api = Blueprint('api', __name__, url_prefix='/api')


restless_preprocessors = {'GET_SINGLE':   [restless_api_auth],
                          'GET_MANY':     [restless_api_auth],
                          'PATCH_SINGLE': [restless_api_auth],
                          'PATCH_MANY':   [restless_api_auth],
                          'PUT_SINGLE':   [restless_api_auth],
                          'PUT_MANY':     [restless_api_auth],
                          'POST':         [restless_api_auth],
                          'DELETE':       [restless_api_auth]}


def configure_restless(app):
    rest.create_api(Campaign, collection_name='campaign', methods=['GET'],
                    include_columns=['id', 'name', 'campaign_type', 'campaign_state', 'campaign_subtype',
                                     'target_ordering', 'allow_call_in', 'call_maximum'],
                    include_methods=['phone_numbers', 'targets', 'status', 'audio_msgs', 'required_fields'])
    rest.create_api(Target, collection_name='target', methods=['GET'],)
    rest.create_api(AudioRecording, collection_name='audiorecording', methods=['GET'],
                    include_columns=['id', 'key', 'version', 'description',
                                     'text_to_speech', 'selected', 'hidden'],
                    include_methods=['file_url', 'selected_campaigns', 'selected_campaign_ids'])

# non CRUD-routes
# protect with decorator
@api.route('/campaign/<int:campaign_id>/stats.json', methods=['GET'])
@api_key_or_auth_required
def campaign_stats(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first_or_404()
    calls_query = (db.session.query(func.date(Call.timestamp), func.count(Call.id))
            .filter(Call.campaign == campaign)
            .group_by(func.date(Call.timestamp))
            .order_by(func.date(Call.timestamp)))
    calls = dict(name='All Calls', data=dict(calls_query.all()))

    series = [calls]

    calls_by_status_query = (
        db.session.query(
            func.date(Call.timestamp),
            Call.status,
            func.count(Call.id)
        )
        .filter(Call.campaign == campaign)
        .group_by(func.date(Call.timestamp))
        .group_by(Call.status)
        .order_by(func.date(Call.timestamp))
    )

    # create a separate series for each status value
    STATUS_LIST = ('completed', 'canceled', 'failed')
    for status in STATUS_LIST:
        data = {}
        # combine status values by date
        for (date, call_status, count) in calls_by_status_query.all():
            # entry like ('2015-08-10', u'canceled', 8)
            if call_status == status:
                data[date] = count
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
