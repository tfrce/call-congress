import hashlib
from datetime import datetime

from ..extensions import db

from .constants import STRING_LEN


class Call(db.Model):
    __tablename__ = 'calls'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)

    # campaign
    campaign_id = db.Column(db.ForeignKey('campaign_campaign.id'))
    campaign = db.relationship('Campaign')

    # target
    target_id = db.Column(db.ForeignKey('campaign_target.id'))
    target = db.relationship('Target')

    # user attributes
    phone_hash = db.Column(db.String(64), nullable=True)  # hashed phone number (optional)
    location = db.Column(db.String(STRING_LEN))  # provided location

    # twilio attributes
    call_id = db.Column(db.String(40))    # twilio call ID
    status = db.Column(db.String(25))     # twilio call status
    duration = db.Column(db.Integer)      # twilio call time in seconds

    @classmethod
    def hash_phone(cls, number):
        """
        Takes a phone number and returns a 64 character string
        """
        return hashlib.sha256(number).hexdigest()

    def __init__(self, campaign_id, target_id, location=None, phone_number=None,
                 call_id=None, status='unknown', duration=0):
        self.timestamp = datetime.now()
        self.status = status
        self.duration = duration
        self.campaign_id = campaign_id
        self.target_id = target_id
        self.call_id = call_id
        self.location = location
        self.phone_hash = self.hash_phone(phone_number)

    def __repr__(self):
        return '<Call to {}>'.format(self.target.name)
