from collections import OrderedDict


API_TIMESPANS = OrderedDict([
    ('minute', '%Y-%m-%d %H:%M'),
    ('hour', '%Y-%m-%d %H:00'),
    ('day', '%Y-%m-%d'),
    # ('week', '%Y W%U'), # format not supported by iso8601.js
    ('month', '%Y-%m'),
    ('year', '%Y')
])
