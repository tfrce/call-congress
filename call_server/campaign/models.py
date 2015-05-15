from datetime import datetime

from sqlalchemy_utils.types import phone_number

from ..extensions import db
from .constants import (CAMPAIGN_CHOICES, STRING_LEN, TWILIO_SID_LENGTH)


class Campaign(db.Model):
    __tablename__ = 'campaign_campaign'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    campaign_type = db.Column(db.String(STRING_LEN))
    campaign_subtype = db.Column(db.String(STRING_LEN))
    allow_call_in = db.Column(db.Boolean)

    target_set = db.relationship(u'Target', secondary=u'campaign_target_sets', backref=db.backref('campaigns'))
    phone_number_set = db.relationship(u'TwilioPhoneNumber', secondary=u'campaign_phone_numbers', backref=db.backref('campaign'))

    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __unicode__(self):
        return self.name


# m2m through tables
t_campaign_target_sets = db.Table(
    u'campaign_target_sets',
    db.Column(u'campaign_id', db.ForeignKey('campaign_campaign.id')),
    db.Column(u'target_id', db.ForeignKey('campaign_target.id'))
)

t_campaign_phone_numbers = db.Table(
    u'campaign_phone_numbers',
    db.Column(u'campaign_id', db.ForeignKey('campaign_campaign.id')),
    db.Column(u'phone_id', db.ForeignKey('campaign_phone.id'), unique=True)
)


class Target(db.Model):
    __tablename__ = 'campaign_target'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    number = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.name


class TwilioPhoneNumber(db.Model):
    __tablename__ = 'campaign_phone'

    id = db.Column(db.Integer, primary_key=True)
    twilio_sid = db.Column(db.String(TWILIO_SID_LENGTH))
    twilio_app = db.Column(db.String(TWILIO_SID_LENGTH))
    number = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.number.__unicode__()

    @classmethod
    def available_numbers(cls, limit=None):
        return TwilioPhoneNumber.query.limit(limit)
