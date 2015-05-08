from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, SelectMultipleField,
                     BooleanField, RadioField)
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from flask_wtf.html5 import IntegerField
from wtforms.validators import Required, AnyOf

from .constants import (CAMPAIGN_CHOICES, CAMPAIGN_NESTED_CHOICES,
                        TARGET_BY_CHOICES, ORDERING_CHOICES,
                        EMPTY_CHOICES)
from ..political_data.constants import US_STATES

from .models import PhoneNumber

from ..utils import choice_items, choice_values, choice_values_flat


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_type = SelectField(_('Campaign Type'), choices=choice_items(CAMPAIGN_CHOICES))
    campaign_state = SelectField(_('State'), choices=choice_items(US_STATES))
    campaign_subtype = SelectField('', [AnyOf(choice_values_flat(CAMPAIGN_NESTED_CHOICES))],
                                       choices=choice_items(EMPTY_CHOICES))
    # nested_type passed to data-field in template, but starts empty

    target_by = RadioField(_('Target By'), choices=choice_items(TARGET_BY_CHOICES))
    target_set = SelectMultipleField(_('or Set Targets'), choices=choice_items(EMPTY_CHOICES))
    target_ordering = RadioField(_('Order'), choices=choice_items(ORDERING_CHOICES))

    call_maximum = IntegerField(_('Call Maximum'))
    no_limit = BooleanField(_('No Limit'))

    phone_numbers = QuerySelectMultipleField(_('Allocate Phone Numbers'),
                                             query_factory=PhoneNumber.available_numbers)
    allow_call_in = BooleanField(_('Allow Call In'))

    submit = SubmitField(_('Next Step'))
