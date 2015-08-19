from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, SelectMultipleField,
                     BooleanField, RadioField, IntegerField,
                     FileField, FieldList, FormField)
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms_components import PhoneNumberField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Optional, AnyOf, NumberRange, ValidationError

from .constants import (CAMPAIGN_CHOICES, CAMPAIGN_NESTED_CHOICES,
                        SEGMENT_BY_CHOICES, LOCATION_CHOICES, ORDERING_CHOICES,
                        CAMPAIGN_STATUS)
from ..political_data.constants import US_STATES

from .models import TwilioPhoneNumber

from ..utils import choice_items, choice_keys, choice_values, choice_values_flat


class TargetForm(Form):
    order = IntegerField(_('Order'),)
    title = TextField(_('Title'), [Optional()])
    name = TextField(_('Name'), [Required()])
    number = PhoneNumberField(_('Phone Number'), [Required()])
    uid = TextField(_('Unique ID'), [Optional()])


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_type = SelectField(_('Campaign Type'), [Required()], choices=choice_items(CAMPAIGN_CHOICES), description=True)
    campaign_state = SelectField(_('State'), [Optional()], choices=choice_items(US_STATES))
    campaign_subtype = SelectField('', [AnyOf(choice_keys(choice_values_flat(CAMPAIGN_NESTED_CHOICES))), Optional()], )
    # nested_type passed to data-field in template, but starts empty

    segment_by = RadioField(_('Segment By'), [Required()], choices=choice_items(SEGMENT_BY_CHOICES),
                            description=True, default=SEGMENT_BY_CHOICES[0][0])
    locate_by = RadioField(_('Locate By'), [Optional()], choices=choice_items(LOCATION_CHOICES),
                                  description=True, default=None)
    target_set = FieldList(FormField(TargetForm, _('Choose Targets')), validators=[Optional()])
    target_ordering = RadioField(_('Order'), choices=choice_items(ORDERING_CHOICES),
                                 description=True, default=ORDERING_CHOICES[0][0])

    call_limit = BooleanField(_('Limit Maximum Calls'), [Optional()], default=False)
    call_maximum = IntegerField(_('Call Maximum'), [Optional(), NumberRange(min=0)])

    phone_number_set = QuerySelectMultipleField(_('Select Phone Numbers'),
                                                query_factory=TwilioPhoneNumber.available_numbers,
                                                validators=[Required()])
    allow_call_in = BooleanField(_('Allow Call In'))

    submit = SubmitField(_('Edit Audio'))

    def validate(self):
        # check default validation
        if not Form.validate(self):
            return False

        # check nested forms
        for t in self.target_set:
            if not t.form.validate():
                error_fields = ','.join(t.form.errors.keys())
                self.target_set.errors.append({'target': t.name, 'message': 'Invalid target ' + error_fields})
                return False

        return True


class CampaignAudioForm(Form):
    next = HiddenField()
    msg_intro = TextField(_('Introduction'))
    msg_location = TextField(_('Location Prompt'))
    msg_intro_location = TextField(_('Introduction with Location'))
    msg_invalid_location = TextField(_('Invalid Location'))
    msg_choose_target = TextField(_('Choose Target'))
    msg_call_block_intro = TextField(_('Call Block Introduction'))
    msg_target_intro = TextField(_('Target Introduction'))
    msg_between_calls = TextField(_('Between Calls'))
    msg_final_thanks = TextField(_('Final Thanks'))

    submit = SubmitField(_('Save and Test'))


class AudioRecordingForm(Form):
    key = TextField(_('Key'), [Required()])
    file_storage = FileField(_('File'), [Optional()])
    text_to_speech = FileField(_('Text to Speech'), [Optional()])
    description = TextField(_('Description'), [Optional()])


class CampaignLaunchForm(Form):
    next = HiddenField()

    test_call_number = TextField(_('Call Me'))

    display_script = TextField(_('Display Script'), widget=TextArea())
    embed_code = TextField(_('Embed Code'), widget=TextArea(), description=True)

    form_selector = TextField(_('Form Selector'))
    display_script_selector = TextField(_('Display Script Selector'))
    success_endpoint = TextField(_('Success Endpoint'))

    submit = SubmitField(_('Launch'))


class CampaignStatusForm(Form):
    status_code = RadioField(_("Status"), [AnyOf([str(val) for val in CAMPAIGN_STATUS.keys()])],
                             choices=[(str(val), label) for val, label in CAMPAIGN_STATUS.items()])
    submit = SubmitField(_('Save'))
