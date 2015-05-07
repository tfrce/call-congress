from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms import (HiddenField, SubmitField, TextField,
                     SelectField, BooleanField, RadioField)
from wtforms.validators import ValidationError, Required

from .constants import (CAMPAIGN_CHOICES, TARGET_BY_CHOICES, )


class CampaignForm(Form):
    next = HiddenField()
    name = TextField(_('Campaign Name'), [Required()])
    campaign_type = SelectField(_('Campaign Type'), choices=CAMPAIGN_CHOICES)
    campaign_nested_type = SelectField(choices=(('', ''),))  # filled in by client

    target_by = RadioField(_('Target By'), choices=TARGET_BY_CHOICES)
    submit = SubmitField(_('Edit Audio'))
