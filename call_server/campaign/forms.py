from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, SelectMultipleField,
                     BooleanField, RadioField, IntegerField,
                     FileField)
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Optional, AnyOf, NumberRange

from .constants import (CAMPAIGN_CHOICES, CAMPAIGN_NESTED_CHOICES,
                        TARGET_BY_CHOICES, ORDERING_CHOICES,
                        EMPTY_CHOICES)
from ..political_data.constants import US_STATES

from .models import Campaign, Target, TwilioPhoneNumber

from ..utils import choice_items, choice_keys, choice_values, choice_values_flat


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_type = SelectField(_('Campaign Type'), choices=choice_items(CAMPAIGN_CHOICES))
    campaign_state = SelectField(_('State'), choices=choice_items(US_STATES))
    campaign_subtype = SelectField('', [AnyOf(choice_keys(choice_values_flat(CAMPAIGN_NESTED_CHOICES)))], )
    # nested_type passed to data-field in template, but starts empty

    target_by = RadioField(_('Target By'), [Optional()], choices=choice_items(TARGET_BY_CHOICES),
                           default=TARGET_BY_CHOICES[0][0])
    target_set = SelectMultipleField(_('Set Targets'), [Optional()] )
    target_ordering = RadioField(_('Order'), choices=choice_items(ORDERING_CHOICES),
                                 default=ORDERING_CHOICES[0][0])

    call_limit = BooleanField(_('Limit Maximum Calls'), [Optional()], default=False)
    call_maximum = IntegerField(_('Call Maximum'), [Optional(), NumberRange(min=0)])

    phone_numbers = QuerySelectMultipleField(_('Allocate Phone Numbers'),
                                             query_factory=TwilioPhoneNumber.available_numbers)
    allow_call_in = BooleanField(_('Allow Call In'))

    submit = SubmitField(_('Next Step'))

    def validate(self):
        passes_default_validation = Form.validate(self)
        if not passes_default_validation:
            return False

        # TODO, custom validation
        # get_one_or_create Target from target_set options

        return True


class CampaignRecordForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    msg_intro = FileField(_('Introduction'))
    msg_location = FileField(_('Location Prompt'))
    msg_invalid_location = FileField(_('Invalid Location'))
    msg_choose_target = FileField(_('Choose Target'))
    msg_between_calls = FileField(_('Between Calls'))
    msg_final_thanks = FileField(_('Final Thanks'))

    display_script = TextField(_('Display Script'), widget=TextArea())
    embed_code = TextField(_('Embed Code'), widget=TextArea())

    success_endpoint = TextField(_('Success Endpoint'))
    form_id = TextField(_('Form ID'))
    display_script_id = TextField(_('Display Script ID'))
