from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, SelectMultipleField,
                     BooleanField, RadioField)
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from flask_wtf.html5 import IntegerField
from wtforms.validators import Required

from .constants import (CAMPAIGN_CHOICES, TARGET_BY_CHOICES, ORDERING_CHOICES,
                        EMPTY_CHOICES)

from .models import PhoneNumber


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_type = SelectField(_('Campaign Type'), choices=CAMPAIGN_CHOICES)
    campaign_nested_type = SelectField('', choices=EMPTY_CHOICES)  # filled in by client

    target_by = RadioField(_('Target By'), choices=TARGET_BY_CHOICES)
    target_set = SelectMultipleField(_('Set Targets'), choices=EMPTY_CHOICES)
    target_ordering = RadioField(_('Order'), choices=ORDERING_CHOICES)

    call_maximum = IntegerField(_('Call Maximum'))
    no_limit = BooleanField(_('No Limit'))

    phone_numbers = QuerySelectMultipleField(_('Allocate Phone Numbers'),
                                             query_factory=PhoneNumber.available_numbers)
    allow_call_in = BooleanField(_('Allow Call In'))

    submit = SubmitField(_('Next Step'))
