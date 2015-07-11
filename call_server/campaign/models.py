from datetime import datetime

from sqlalchemy_utils.types import phone_number
from flask_store.sqla import FlaskStoreType

from ..extensions import db
from ..utils import convert_to_dict, choice_values_flat
from .constants import (CAMPAIGN_CHOICES, CAMPAIGN_NESTED_CHOICES, STRING_LEN, TWILIO_SID_LENGTH,
                        CAMPAIGN_STATUS, PAUSED)


class Campaign(db.Model):
    __tablename__ = 'campaign_campaign'

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    campaign_type = db.Column(db.String(STRING_LEN))
    campaign_state = db.Column(db.String(STRING_LEN))
    campaign_subtype = db.Column(db.String(STRING_LEN))

    segment_by = db.Column(db.String(STRING_LEN))
    target_set = db.relationship('Target', secondary='campaign_target_sets',
                                 order_by='campaign_target_sets.c.order',
                                 backref=db.backref('campaign'))
    target_ordering = db.Column(db.String(STRING_LEN))

    allow_call_in = db.Column(db.Boolean, default=False)
    phone_number_set = db.relationship('TwilioPhoneNumber', secondary='campaign_phone_numbers',
                                       backref=db.backref('campaign', uselist=False))
    call_maximum = db.Column(db.SmallInteger, nullable=True)

    status_code = db.Column(db.SmallInteger, default=PAUSED)

    @property
    def status(self):
        return CAMPAIGN_STATUS.get(self.status_code, '')

    def __unicode__(self):
        return self.name

    def campaign_type_display(self):
        campaign_choices = convert_to_dict(CAMPAIGN_CHOICES)
        campaign_subchoices = convert_to_dict(choice_values_flat(CAMPAIGN_NESTED_CHOICES))
        val = ''
        if self.campaign_type:
            val = campaign_choices.get(self.campaign_type, '')
        if self.campaign_subtype and self.campaign_subtype != "None":
            sub = campaign_subchoices.get(self.campaign_subtype, '')
            val = '%s - %s' % (val, sub)
            if self.campaign_type == 'state':
                #special case, show specific state
                val = '%s - %s' % (self.campaign_state, sub)

        return val

    def targets_list(self):
        return ['%s %s' % (s.name, s.number) for s in self.target_set]

    def target_set_display(self):
        return "<br>".join(self.targets_list())

    def phone_number_list(self):
        return [str(n.number) for n in self.phone_number_set]

    def audio(self, key):
        # convenience method for getting the selected audio recording by key
        return AudioRecording.query.filter_by(campaign_id=self.id, key=key, selected=True).first()

    @classmethod
    def duplicate(self):
        arguments = dict()
        for name, column in self.__mapper__.columns.items():
            if not (column.primary_key or column.unique):
                arguments[name] = getattr(self, name)
        return self.__class__(**arguments)


class CampaignTarget(db.Model):
    __tablename__ = 'campaign_target_sets'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign_campaign.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('campaign_target.id'))
    order = db.Column(db.Integer())

    campaign = db.relationship('Campaign', backref='campaigntargets')
    target = db.relationship('Target', backref='campaigntargets')


class CampaignPhoneNumber(db.Model):
    __tablename__ = 'campaign_phone_numbers'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign_campaign.id'))
    phone_id = db.Column(db.Integer, db.ForeignKey('campaign_phone.id'), unique=False)


class Target(db.Model):
    __tablename__ = 'campaign_target'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(STRING_LEN), nullable=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=False)
    number = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.name

    def full_name(self):
        return unicode("{} {}".format(self.title, self.name), 'utf8')


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


class AudioRecording(db.Model):
    __tablename__ = 'campaign_recording'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(STRING_LEN), nullable=False)

    file_storage = db.Column(FlaskStoreType(location='audio/'), nullable=True)
    text_to_speech = db.Column(db.Text)
    version = db.Column(db.Integer, unique=True)
    description = db.Column(db.String(STRING_LEN))

    campaign = db.relationship('Campaign', secondary='campaign_audio_recordings',
                               backref=db.backref('audiorecording'))

    def file_url(self):
        if self.file_storage:
            return self.file_storage.absolute_url
        else:
            return None

    def __unicode__(self):
        return "%s v%s" % (self.key, self.version)


class CampaignAudioRecording(db.Model):
    __tablename__ = 'campaign_audio_recordings'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign_campaign.id'))
    recording_id = db.Column(db.Integer, db.ForeignKey('campaign_recording.id'))
    selected = db.Column(db.Boolean, default=False)

