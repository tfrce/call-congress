from ..campaign.constants import (TYPE_CONGRESS, LOCATION_POSTAL, LOCATION_LATLNG,
    ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)

from ..extensions import cache
from countries.us import USData

# initialize data for all relevant countries
COUNTRY_DATA = {
    'US': USData(cache)
}


def locate_targets(location, country='US', campaign_type=TYPE_CONGRESS,
                    segment_by=LOCATION_POSTAL, order_by=ORDER_IN_ORDER):

    data = COUNTRY_DATA[country]

    if country is 'US' and campaign_type is TYPE_CONGRESS:
        if segment_by is LOCATION_POSTAL:
            return data.get_congress_targets(zipcode=location, order_by=order_by)
        # elif segment_by is LOCATION_LATLNG:
        #    TODO lookup target from latlng
        #    return locate_targets_by_latlng(location, cache)

    else:
        # not yet implemented
        return []
