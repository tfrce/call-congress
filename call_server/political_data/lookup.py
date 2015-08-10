from ..campaign.constants import (TYPE_CONGRESS, LOCATION_POSTAL, LOCATION_LATLNG,
    ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)

from ..extensions import cache
from countries.us import USData

# initialize data for all relevant countries
COUNTRY_DATA = {
    'US': USData(cache)
}


def locate_targets(location, campaign):
    if campaign.target_set:
        return campaign.target_set

    if campaign.campaign_type == TYPE_CONGRESS:
        data = COUNTRY_DATA['US']
        if campaign.locate_by == LOCATION_POSTAL:
            return data.locate_member_ids(zipcode=location,
                chambers=campaign.campaign_subtype,
                order=campaign.target_ordering)
        # elif campaign.locate_by == LOCATION_LATLNG:
        #    TODO lookup target from latlng
        #    return data.locate_member_ids(latlng=location, order=campaign.target_ordering)
        else:
            raise NotImplementedError('campaign has unknown locate_by value: %s' % campaign.locate_by)


    # elif campaign.type == TYPE_EXECUTIVE
        # Whitehouse number?
    # elif campaign.type == TYPE_STATE
        # state-level data from sunlight?

    else:
        # not yet implemented
        return []
