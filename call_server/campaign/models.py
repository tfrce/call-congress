from datetime import datetime

from flask import current_app
from sqlalchemy_utils.types import phone_number
from flask_store.sqla import FlaskStoreType
from sqlalchemy import UniqueConstraint

from ..extensions import db, cache
from ..utils import convert_to_dict
from ..political_data.adapters import adapt_to_target
from .constants import (CAMPAIGN_CHOICES, CAMPAIGN_NESTED_CHOICES, STRING_LEN, TWILIO_SID_LENGTH,
                        CAMPAIGN_STATUS, STATUS_PAUSED, SEGMENT_BY_CHOICES, LOCATION_CHOICES, ORDERING_CHOICES, )


class Campaign(db.Model):
    __tablename__ = 'campaign_campaign'

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    name = db.Column(db.String(STRING_LEN), nullable=False, unique=True)
    campaign_type = db.Column(db.String(STRING_LEN))
    campaign_state = db.Column(db.String(STRING_LEN))
    campaign_subtype = db.Column(db.String(STRING_LEN))

    segment_by = db.Column(db.String(STRING_LEN))
    locate_by = db.Column(db.String(STRING_LEN))
    target_set = db.relationship('Target', secondary='campaign_target_sets',
                                 order_by='campaign_target_sets.c.order',
                                 backref=db.backref('campaigns'))
    target_ordering = db.Column(db.String(STRING_LEN))

    allow_call_in = db.Column(db.Boolean, default=False)
    phone_number_set = db.relationship('TwilioPhoneNumber', secondary='campaign_phone_numbers',
                                       backref=db.backref('campaigns'))
    call_maximum = db.Column(db.SmallInteger, nullable=True)

    audio_recordings = db.relationship('AudioRecording', secondary='campaign_audio_recordings',
                                       backref=db.backref('campaigns'))

    status_code = db.Column(db.SmallInteger, default=STATUS_PAUSED)

    @property
    def status(self):
        return CAMPAIGN_STATUS.get(self.status_code, '')

    def __unicode__(self):
        return self.name

    def audio(self, key):
        "Convenience method for getting selected audio recordings for this campaign by key "
        campaignAudio = self._audio_query().filter(
            CampaignAudioRecording.recording.has(key=key)
        ).first()

        if campaignAudio:
            return campaignAudio.recording
        else:
            # if not defined by user, return default
            return current_app.config.CAMPAIGN_MESSAGE_DEFAULTS.get(key)

    def audio_msgs(self):
        "Convenience method for getting all selected audio recordings for this campaign"
        table = {}
        for r in self._audio_query().all():
            table[r.recording.key] = r.recording.file_url()
        return table

    def _audio_query(self):
        return CampaignAudioRecording.query.filter(
            CampaignAudioRecording.campaign_id == self.id,
            CampaignAudioRecording.selected == True)

    def campaign_type_display(self):
        "Display method for this campaign's type"
        campaign_choices = convert_to_dict(CAMPAIGN_CHOICES)
        val = ''
        if self.campaign_type:
            val = campaign_choices.get(self.campaign_type, '')

        return val

    def campaign_subtype_display(self):
        "Display method for this campaign's subtype"
        subtype_choices = convert_to_dict(CAMPAIGN_NESTED_CHOICES)
        campaign_subtypes = dict(subtype_choices[self.campaign_type])
        val = ''
        if self.campaign_subtype and self.campaign_subtype != "None":
            sub = campaign_subtypes.get(self.campaign_subtype, '')
            if self.campaign_type == 'state':
                # special case, show specific state
                val = '%s - %s' % (self.campaign_state, sub)
            else:
                val = sub
        return val

    def phone_numbers(self, region_code=None):
        "Phone numbers for this campaign, can be limited to a specified region code (ISO-2)"
        if region_code:
            # convert region_code to country_code for comparison
            country_code = phone_number.phonenumbers.country_code_for_region(region_code)
            return [n.number.national for n in self.phone_number_set if n.number.country_code == country_code]
        else:
            # return all numbers in set
            return [n.number.national for n in self.phone_number_set]

    def required_fields(self):
        """API convenience method for rendering campaigns externally
        Returns dict of parameters and data types required to place call"""
        fields = {'userPhone': 'US'}  # TODO, update for multiple countries
        if self.segment_by == 'location':
            fields.update({'userLocation': self.locate_by})
        return fields

    def segment_display(self):
        "Display method for this campaign's segmenting and locating of callers"
        val = dict(SEGMENT_BY_CHOICES)[self.segment_by]
        if self.segment_by == 'location':
            val = '%s - %s' % (val, dict(LOCATION_CHOICES)[self.locate_by])
        return val

    def targets(self):
        "Convenience method for getting list of target names and phone numbers"
        return [(s.name, str(s.number)) for s in self.target_set]

    def targets_display(self):
        "Display method for this campaign's target list if specified, or subtype (like Congress - Senate)"
        if self.target_set:
            return "<br>".join(["%s %s" % (t) for t in self.targets()])
        else:
            return self.campaign_subtype_display()


class CampaignTarget(db.Model):
    __tablename__ = 'campaign_target_sets'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign_campaign.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('campaign_target.id'))
    order = db.Column(db.Integer())

    campaign = db.relationship('Campaign', backref='campaign_targets')
    target = db.relationship('Target', backref='campaign_targets')


class CampaignPhoneNumber(db.Model):
    __tablename__ = 'campaign_phone_numbers'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign_campaign.id'))
    phone_id = db.Column(db.Integer, db.ForeignKey('campaign_phone.id'), unique=False)


class Target(db.Model):
    __tablename__ = 'campaign_target'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(STRING_LEN), index=True, nullable=True)  # for US, this is bioguide_id
    title = db.Column(db.String(STRING_LEN), nullable=True)
    name = db.Column(db.String(STRING_LEN), nullable=False, unique=False)
    number = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.name

    def full_name(self):
        return unicode("{} {}".format(self.title, self.name), 'utf8')

    @classmethod
    def get_uid_or_cache(cls, uid, key_prefix="us:bioguide"):
        t = Target.query.filter(Target.uid == uid).first()
        cached = False

        if not t:
            key = '%s:%s' % (key_prefix, uid)
            cache_list = cache.get(key)
            if cache_list:
                # TODO, check to ensure it is list-like
                obj = cache_list[0]
                data = adapt_to_target(obj, key_prefix)

                # create target object and save for reuse
                t = Target(**data)
                cached = True
        return t, cached


class TwilioPhoneNumber(db.Model):
    __tablename__ = 'campaign_phone'

    id = db.Column(db.Integer, primary_key=True)
    twilio_sid = db.Column(db.String(TWILIO_SID_LENGTH))
    twilio_app = db.Column(db.String(TWILIO_SID_LENGTH))
    call_in_allowed = db.Column(db.Boolean, default=False)
    number = db.Column(phone_number.PhoneNumberType())

    def __unicode__(self):
        return self.number.__unicode__()

    @classmethod
    def available_numbers(cls, limit=None):
        # returns all numbers which do not have call_in_allowed
        #return TwilioPhoneNumber.query.filter_by(call_in_allowed=False).limit(limit)
        return TwilioPhoneNumber.query.limit(limit)


class AudioRecording(db.Model):
    __tablename__ = 'campaign_recording'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(STRING_LEN), nullable=False)

    file_storage = db.Column(FlaskStoreType(location='audio/'), nullable=True)
    text_to_speech = db.Column(db.Text)
    version = db.Column(db.Integer)
    description = db.Column(db.String(STRING_LEN))

    hidden = db.Column(db.Boolean, default=False)

    __table_args__ = (UniqueConstraint('key', 'version'),)

    def file_url(self):
        if self.file_storage:
            return self.file_storage.absolute_url
        else:
            return None

    def selected_recordings(self):
        return self.campaign_audio_recordings.filter_by(selected=True).all()

    def selected_campaigns(self):
        names = [s.campaign.name for s in self.selected_recordings()]
        return ','.join(names)

    def selected_campaign_ids(self):
        ids = [s.campaign.id for s in self.selected_recordings()]
        return ids

    def __unicode__(self):
        return "%s v%s" % (self.key, self.version)


class CampaignAudioRecording(db.Model):
    __tablename__ = 'campaign_audio_recordings'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign_campaign.id'))
    recording_id = db.Column(db.Integer, db.ForeignKey('campaign_recording.id'))
    selected = db.Column(db.Boolean, default=False)

    campaign = db.relationship('Campaign')
    recording = db.relationship('AudioRecording', backref=db.backref('campaign_audio_recordings',
                                                                     lazy='dynamic'))
