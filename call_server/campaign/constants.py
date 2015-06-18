# Campaign types
EXECUTIVE = 'executive'
CONGRESS = 'congress'
STATE = 'state'
LOCAL = 'local'
CUSTOM = 'custom'

CAMPAIGN_CHOICES = (
    ('', ''),
    (EXECUTIVE, 'Executive'),
    (CONGRESS, 'Congress'),
    (STATE, 'State'),
    (LOCAL, 'Local'),
    (CUSTOM, 'Custom'),
)
CAMPAIGN_NESTED_CHOICES = (
    ('', ''),
    (EXECUTIVE, (('president', 'President'), ('office', 'Office'))),
    (CONGRESS, (('both', 'Both Bodies'), ('senate', 'Senate Only'), ('house', 'House Only'))),
    (STATE, (('both', 'Both Bodies'), ('upper', 'Upper Body'), ('lower', 'Lower Body'), ('governor', 'Governor'))),
    (LOCAL, ()),
    (CUSTOM, ()),
)

# these types of campaigns cannot be looked up via api
# default to the custom target interface
CUSTOM_CAMPAIGN_CHOICES = [
    'executive.office',
    'local',
    'custom'
]

SEGMENT_BY_CHOICES = (
    ('', 'None'),
    ('location', 'Location'),
    ('other', 'Other')
)

LOCATION_CHOICES = (
    ('', 'None'),
    ('postal', 'ZIP / Postal Code'),
    ('latlng', 'Lat / Lon')
)

ORDERING_CHOICES = (
    ('in-order', 'In Order'),
    ('shuffle', 'Shuffle'),
    ('senate-first', 'Senate First'),
    ('house-first', 'House First'),
)

ARCHIVED = 0
PAUSED = 1
LIVE = 2
CAMPAIGN_STATUS = {
    ARCHIVED: 'archived',
    PAUSED: 'paused',
    LIVE: 'live',
}

# empty set of choices, for filling in on client-side
EMPTY_CHOICES = {'': ''}

STRING_LEN = 100
TWILIO_SID_LENGTH = 34

import yaml
FIELD_DESCRIPTIONS = yaml.load(open('call_server/campaign/field_descriptions.yaml'))
