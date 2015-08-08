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
    (STATE, (('governor', 'Governor'),
             ('both', 'Legislature - Both Bodies'), ('upper', 'Legislature - Upper Body'), ('lower', 'Legislature - Lower Body')
             )),
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
    ('location', 'Location'),
    ('custom', 'Custom')
)

LOCATION_POSTAL = 'postal'
LOCATION_LATLNG = 'latlng'
LOCATION_CHOICES = (
    (LOCATION_POSTAL, 'ZIP / Postal Code'),
    (LOCATION_LATLNG, 'Lat / Lon')
)

ORDER_IN_ORDER = 'in-order'
ORDER_SHUFFLE = 'shuffle'
ORDER_SENATE_FIRST = 'senate-first'
ORDER_HOUSE_FIRST = 'house-first'
ORDERING_CHOICES = (
    (ORDER_IN_ORDER, 'In Order'),
    (ORDER_SHUFFLE, 'Shuffle'),
    (ORDER_SENATE_FIRST, 'Senate First'),
    (ORDER_HOUSE_FIRST, 'House First'),
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
