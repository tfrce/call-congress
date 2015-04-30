# -*- coding: utf-8 -*-

# User roles
ADMIN = 0    # edit all
STAFF = 1    # edit all campaigns
PARTNER = 2  # edit own campaigns
VIEWER = 3   # view stats only
USER_ROLE = {
    ADMIN: 'admin',
    STAFF: 'staff',
    PARTNER: 'partner',
    VIEWER: 'viewer'
}

# User status
INACTIVE = 0
NEW = 1
ACTIVE = 2
USER_STATUS = {
    INACTIVE: 'inactive',
    NEW: 'new',
    ACTIVE: 'active',
}

STRING_LEN = 100

USERNAME_LEN_MIN = 4
USERNAME_LEN_MAX = 25

REALNAME_LEN_MIN = 4
REALNAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 16
