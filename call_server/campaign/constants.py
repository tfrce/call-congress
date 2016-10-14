# Campaign types
TYPE_EXECUTIVE = 'executive'
TYPE_CONGRESS = 'congress'
TYPE_STATE = 'state'
TYPE_LOCAL = 'local'
TYPE_CUSTOM = 'custom'

TARGET_EXECUTIVE = 'exec'
TARGET_OFFICE = 'office'
TARGET_CHAMBER_BOTH = 'both'
TARGET_CHAMBER_UPPER = 'upper'
TARGET_CHAMBER_LOWER = 'lower'

CAMPAIGN_CHOICES = (
    ('', ''),
    (TYPE_EXECUTIVE, 'Executive'),
    (TYPE_CONGRESS, 'Congress'),
    (TYPE_STATE, 'State'),
    (TYPE_LOCAL, 'Local'),
    (TYPE_CUSTOM, 'Custom'),
)
CAMPAIGN_NESTED_CHOICES = (
    ('', ''),
    (TYPE_EXECUTIVE, (
        (TARGET_EXECUTIVE, 'President'),
        (TARGET_OFFICE, 'Office')
    )),
    (TYPE_CONGRESS, (
        (TARGET_CHAMBER_BOTH, 'Both Bodies'),
        (TARGET_CHAMBER_UPPER, 'Senate Only'),
        (TARGET_CHAMBER_LOWER, 'House Only')
    )),
    (TYPE_STATE, (
        (TARGET_EXECUTIVE, 'Governor'),
        (TARGET_CHAMBER_BOTH, 'Legislature - Both Bodies'),
        (TARGET_CHAMBER_UPPER, 'Legislature - Upper Body'),
        (TARGET_CHAMBER_LOWER, 'Legislature - Lower Body')
    )),
    (TYPE_LOCAL, ()),
    (TYPE_CUSTOM, ()),
)

# these types of campaigns cannot be looked up via api
# default to the custom target interface
CUSTOM_CAMPAIGN_CHOICES = [
    'executive.office',
    'local',
    'custom'
]

SEGMENT_BY_LOCATION = 'location'
SEGMENT_BY_CUSTOM = 'custom'
SEGMENT_BY_CHOICES = (
    (SEGMENT_BY_LOCATION, 'Location'),
    (SEGMENT_BY_CUSTOM, 'Custom')
)

LOCATION_POSTAL = 'postal'
LOCATION_ADDRESS = 'address'
LOCATION_LATLON = 'latlon'
LOCATION_DISTRICT = 'district'
LOCATION_CHOICES = (
    ('', 'None'),
    (LOCATION_POSTAL, 'ZIP / Postal Code'),
    (LOCATION_ADDRESS, 'Street Address'),
    (LOCATION_LATLON, 'Lat / Lon'),
    (LOCATION_DISTRICT, 'District')
)

ORDER_IN_ORDER = 'in-order'
ORDER_SHUFFLE = 'shuffle'
ORDER_UPPER_FIRST = 'upper-first'
ORDER_LOWER_FIRST = 'lower-first'
ORDERING_CHOICES = (
    (ORDER_IN_ORDER, 'In Order'),
    (ORDER_SHUFFLE, 'Shuffle'),
    (ORDER_UPPER_FIRST, 'Senate First'),
    (ORDER_LOWER_FIRST, 'House First'),
)

STATUS_ARCHIVED = 0
STATUS_PAUSED = 1
STATUS_LIVE = 2
CAMPAIGN_STATUS = {
    STATUS_ARCHIVED: 'archived',
    STATUS_PAUSED: 'paused',
    STATUS_LIVE: 'live',
}

EMBED_FORM_CHOICES = (
    ('', 'None'),
    ('iframe', 'iFrame'),
    ('custom', 'Custom'),
)

EMBED_SCRIPT_DISPLAY = (
    ('', 'None'),
    ('overlay', 'Overlay'),
    ('replace', 'Replace Form'),
    ('custom', 'Custom')
)


# empty set of choices, for filling in on client-side
EMPTY_CHOICES = {'': ''}

STRING_LEN = 100
TWILIO_SID_LENGTH = 34
