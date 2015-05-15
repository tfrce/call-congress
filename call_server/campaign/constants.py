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

TARGET_BY_CHOICES = (
    ('zipcode', 'Zipcode'),
    ('lat_lon', 'Lat / Lon'),
    ('form_param', 'Form Parameter'),
    ('custom', 'Custom')
)

ORDERING_CHOICES = (
    ('in-order', 'In Order'),
    ('shuffle', 'Shuffle'),
)

# empty set of choices, for filling in on client-side
EMPTY_CHOICES = {'': ''}

STRING_LEN = 100
TWILIO_SID_LENGTH = 34
