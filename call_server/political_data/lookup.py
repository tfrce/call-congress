from ..campaign.constants import (TYPE_CONGRESS, TYPE_STATE,
    LOCATION_POSTAL, LOCATION_LATLNG,
    ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)

from ..extensions import cache
from countries.us import USData
from countries.us_state import USStateData

# initialize data for all relevant countries
COUNTRY_DATA = {
    'US': USData(cache),
    'USState': USStateData(cache, api_cache='localmem')  # TODO, wrap sunlight cache for flask
}


def locate_targets(location, campaign):
    """ Locate targets for location for a given campaign.
    Returns list of target uids """
    if campaign.target_set:
        return [t.uid for t in campaign.target_set]

    if campaign.campaign_type == TYPE_CONGRESS:
        data = COUNTRY_DATA['US']
        if campaign.locate_by == LOCATION_POSTAL:
            return data.locate_targets(zipcode=location,
                chambers=campaign.campaign_subtype,
                order=campaign.target_ordering)
        # elif campaign.locate_by == LOCATION_LATLNG:
        #    TODO lookup target from latlng
        #    return data.locate_member_ids(latlon=location, order=campaign.target_ordering)
        else:
            raise NotImplementedError('campaign has unknown locate_by value: %s' % campaign.locate_by)

    # elif campaign.campaign_type == TYPE_EXECUTIVE
        # Whitehouse number?
    elif campaign.campaign_type == TYPE_STATE:
        data = COUNTRY_DATA['USState']
        # state-level data from sunlight
        if campaign.locate_by == LOCATION_LATLNG:
            return data.locate_targets(latlon=location,
                chambers=campaign.campaign_subtype,
                order=campaign.target_ordering)
        else:
            raise NotImplementedError('state campaigns, invalid locate_by value: %s' % campaign.locate_by)
    else:
        # not yet implemented
        return []
