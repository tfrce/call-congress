# -*- coding: utf-8 -*-

# User roles
USER_ADMIN = 0    # edit users
USER_STAFF = 1    # edit all campaigns
USER_PARTNER = 2  # edit own campaigns
USER_VIEWER = 3   # view stats only
USER_ROLE = {
    USER_ADMIN: 'admin',
    USER_STAFF: 'staff',
    USER_PARTNER: 'partner',
    USER_VIEWER: 'viewer'
}

# User status
USER_INACTIVE = 0
USER_NEW = 1
USER_ACTIVE = 2
USER_STATUS = {
    USER_INACTIVE: 'inactive',
    USER_NEW: 'new',
    USER_ACTIVE: 'active',
}

STRING_LEN = 100

USERNAME_LEN_MIN = 4
USERNAME_LEN_MAX = 25

REALNAME_LEN_MIN = 4
REALNAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 64
