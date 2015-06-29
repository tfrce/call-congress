from flask.ext.login import current_user
from flask.ext.restless import ProcessingException

from ..extensions import rest
from ..campaign.models import Campaign, Target, AudioRecording


def restless_api_auth(*args, **kwargs):
    if current_user.is_authenticated():
        return None  # allow

    # TODO, check for system api key

    raise ProcessingException(message='Not authenticated!')

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
                                     'target_ordering', 'allow_call_in', 'call_maximum', ],
                    include_methods=['phone_number_list', 'targets_list', 'status'])
    rest.create_api(Target, collection_name='target', methods=['GET'],)
    rest.create_api(AudioRecording, collection_name='recording', methods=['GET'],
                    include_columns=['id', 'key', 'version', 'description',
                                     'text_to_speech', 'selected'],
                    include_methods=['file_url', 'campaign_name'])
