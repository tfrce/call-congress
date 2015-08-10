import json
from flask import Blueprint, Response
from sqlalchemy.sql import func

from decorators import api_key_or_auth_required, restless_api_auth

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
    calls_by_day_query = (db.session.query(func.date(Call.timestamp), func.count(Call.id))
            .filter(Call.campaign == campaign)
            .group_by(func.date(Call.timestamp)))
    calls_by_day = dict(name='Calls by Day', data=dict(calls_by_day_query.all()))

    total_calls_query = Call.query.filter(Call.campaign == campaign)
    total_calls = dict(name='Total Calls', data=total_calls_query.count())

    return Response(json.dumps([total_calls, calls_by_day]), mimetype='application/json')
