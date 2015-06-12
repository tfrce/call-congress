from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, SelectMultipleField,
                     BooleanField, RadioField, IntegerField,
                     FileField, FieldList, FormField)
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms_components import PhoneNumberField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Optional, AnyOf, NumberRange

from .constants import (CAMPAIGN_CHOICES, CAMPAIGN_NESTED_CHOICES,
                        SEGMENT_BY_CHOICES, ORDERING_CHOICES,
                        CAMPAIGN_STATUS)
from ..political_data.constants import US_STATES

from .models import Campaign, Target, TwilioPhoneNumber

from ..utils import choice_items, choice_keys, choice_values, choice_values_flat


class TargetForm(Form):
    order = IntegerField(_('Order'),)
    title = TextField(_('Title'), [Optional()])
    name = TextField(_('Name'), [Required()])
    number = PhoneNumberField(_('Phone Number'), [Required()])


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_type = SelectField(_('Campaign Type'), [Required()], choices=choice_items(CAMPAIGN_CHOICES),
                                description="Campaign targets which decision making body?")
    campaign_state = SelectField(_('State'), [Optional()], choices=choice_items(US_STATES))
    campaign_subtype = SelectField('', [AnyOf(choice_keys(choice_values_flat(CAMPAIGN_NESTED_CHOICES))), Optional()], )
    # nested_type passed to data-field in template, but starts empty

    segment_by = RadioField(_('Segment By'), [Optional()], choices=choice_items(SEGMENT_BY_CHOICES),
                            default=SEGMENT_BY_CHOICES[0][0],
                            description="Segment callers by geography or custom ordering.")
    target_set = FieldList(FormField(TargetForm, _('Choose Targets')),
                           description="Lookup target phone numbers in Sunlight, or add them directly.",
                           validators=[Optional()])
    target_ordering = RadioField(_('Order'), choices=choice_items(ORDERING_CHOICES),
                                 default=ORDERING_CHOICES[0][0])

    call_limit = BooleanField(_('Limit Maximum Calls'), [Optional()], default=False)
    call_maximum = IntegerField(_('Call Maximum'), [Optional(), NumberRange(min=0)])

    phone_number_set = QuerySelectMultipleField(_('Allocate Phone Numbers'),
                                                query_factory=TwilioPhoneNumber.available_numbers)
    allow_call_in = BooleanField(_('Allow Call In'))

    submit = SubmitField(_('Edit Audio'))

    def validate(self):
        passes_default_validation = Form.validate(self)
        if not passes_default_validation:
            return False

        # correct data for related fields
        if self.call_maximum:
            self.call_limit = True

        # get_one_or_create Target from target_set?

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

    submit = SubmitField(_('Save and Activate'))


class CampaignStatusForm(Form):
    status_code = RadioField(_("Status"), [AnyOf([str(val) for val in CAMPAIGN_STATUS.keys()])],
                             choices=[(str(val), label) for val, label in CAMPAIGN_STATUS.items()])
    submit = SubmitField(_('Save'))
