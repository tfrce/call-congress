from datetime import datetime

from sqlalchemy_utils.types import phone_number

from ..extensions import db
from .constants import (CAMPAIGN_CHOICES, STRING_LEN)


class Campaign(db.Model):
    __tablename__ = 'campaign_campaign'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    type = db.Column(db.Integer)
    target_set = db.relationship(u'Target', secondary=u'campaign_target_sets', backref=db.backref('campaigns'))
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __unicode__(self):
        return self.name


t_campaign_target_sets = db.Table(
    u'campaign_target_sets',
    db.Column(u'campaign_id', db.ForeignKey('campaign_campaign.id')),
    db.Column(u'target_id', db.ForeignKey('campaign_target.id'))
)


class Target(db.Model):
    __tablename__ = 'campaign_target'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    number = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.name


class PhoneNumber(db.Model):
    __tablename__ = 'campaign_phone'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.phone
