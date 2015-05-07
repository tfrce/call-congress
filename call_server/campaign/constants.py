# Campaign types
EXECUTIVE = 0
CONGRESS = 1
STATE = 2
LOCAL = 3
CUSTOM = 4

CAMPAIGN_CHOICES = (
    (EXECUTIVE, 'Executive'),
    (CONGRESS, 'Congress'),
    (STATE, 'State'),
    (LOCAL, 'Local'),
    (CUSTOM, 'Custom'),
)
CAMPAIGN_NESTED_CHOICES = {
    EXECUTIVE: ['President', 'Office'],
    CONGRESS: ['Senate', 'House'],
    STATE: ['Senate', 'House', 'Governor'],
    LOCAL: None,
    CUSTOM: None
}

TARGET_BY_CHOICES = (
    ('zipcode', 'Zipcode'),
    ('lat_lon', 'Lat / Lon'),
    ('form_param', 'Form Parameter')
)

STRING_LEN = 100
