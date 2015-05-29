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
    (CONGRESS, (('senate', 'Senate'), ('house', 'House'))),
    (STATE, (('upper', 'Senate'), ('lower', 'House'), ('governor', 'Governor'))),
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

TARGET_BY_CHOICES = (
    ('zipcode', 'Zipcode'),
    ('lat_lon', 'Lat / Lon'),
    ('custom', 'Custom')
)

ORDERING_CHOICES = (
    ('in-order', 'In Order'),
    ('shuffle', 'Shuffle'),
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
