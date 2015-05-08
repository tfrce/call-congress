# Campaign types
EXECUTIVE = 'executive'
CONGRESS = 'congress'
STATE = 'state'
LOCAL = 'local'
CUSTOM = 'custom'

CAMPAIGN_CHOICES = {
    '': '',
    EXECUTIVE: 'Executive',
    CONGRESS: 'Congress',
    STATE: 'State',
    LOCAL: 'Local',
    CUSTOM: 'Custom',
}
CAMPAIGN_NESTED_CHOICES = {
    '': '',
    EXECUTIVE: ['President', 'Office'],
    CONGRESS: ['Senate', 'House'],
    STATE: ['Senate', 'House', 'Governor'],
    LOCAL: [None],
    CUSTOM: [None],
}

TARGET_BY_CHOICES = {
    'zipcode': 'Zipcode',
    'lat_lon': 'Lat / Lon',
    'form_param': 'Form Parameter',
}

ORDERING_CHOICES = {
    'in-order': 'In Order',
    'shuffle': 'Shuffle',
}

# empty set of choices, for filling in on client-side
EMPTY_CHOICES = {'': ''}

STRING_LEN = 100
