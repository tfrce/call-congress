from ..campaign.constants import (TYPE_CONGRESS, TYPE_STATE, TYPE_EXECUTIVE,
    TARGET_EXECUTIVE, TARGET_CHAMBER_BOTH, TARGET_CHAMBER_UPPER, TARGET_CHAMBER_LOWER,
    LOCATION_POSTAL, LOCATION_ADDRESS, LOCATION_DISTRICT, LOCATION_LATLON,
    ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)

from ..extensions import cache
from countries.us import USData
from countries.us_state import USStateData
from geocode import Geocoder

# initialize data for all relevant countries
COUNTRY_DATA = {
    'US': USData(cache),
    'USState': USStateData(cache, api_cache='localmem')
}

GEOCODER = Geocoder()


def locate_targets(location, campaign):
    """ Locate targets for location for a given campaign.
    Returns list of target uids """
    if campaign.target_set:
        return [t.uid for t in campaign.target_set]

    if campaign.campaign_type == TYPE_CONGRESS:
        data = COUNTRY_DATA['US']
        if campaign.locate_by == LOCATION_DISTRICT:
            (state, district) = location.split("-")
            district = "0" if district == "AL" else district

            return data.locate_targets(state=state, district=int(district),
                chambers=campaign.campaign_subtype,
                order=campaign.target_ordering)
        elif campaign.locate_by == LOCATION_POSTAL:
            return data.locate_targets(zipcode=location,
                chambers=campaign.campaign_subtype,
                order=campaign.target_ordering)
        # elif campaign.locate_by == LOCATION_LATLON:
        #    TODO lookup target from latlon
        #    return data.locate_member_ids(latlon=location, order=campaign.target_ordering)
        else:
            raise NotImplementedError('campaign has unknown locate_by value: %s' % campaign.locate_by)

    elif campaign.campaign_type == TYPE_EXECUTIVE:
        data = COUNTRY_DATA['US']
        return data.get_executive()

    elif campaign.campaign_type == TYPE_STATE:
        data = COUNTRY_DATA['USState']

        if campaign.locate_by == LOCATION_POSTAL:
            geocoded = GEOCODER.zipcode(location)
        elif campaign.locate_by == LOCATION_ADDRESS:
            geocoded = GEOCODER.geocode(location)
        elif campaign.locate_by == LOCATION_LATLON:
            geocoded = GEOCODER.reverse(location)
        else:
            geocoded = False

        if campaign.campaign_subtype == TARGET_EXECUTIVE:
            if campaign.campaign_state:
                # default to specified campaign state specified
                return data.locate_governor(state=campaign.campaign_state)
            else:
                # if no state specified, route via geocoding
                if geocoded:
                    return data.locate_governor(state=geocoded.state)
                else:
                    return []

        if campaign.campaign_subtype in (TARGET_CHAMBER_BOTH, TARGET_CHAMBER_UPPER, TARGET_CHAMBER_LOWER):
            if geocoded:
                return data.locate_targets(latlon=geocoded.location,
                    chambers=campaign.campaign_subtype,
                    order=campaign.target_ordering,
                    state=campaign.campaign_state)
            else:
                return []

        else:
            raise NotImplementedError('invalid campaign subtype: %s' % campaign.campaign_subtype)
    else:
        # not yet implemented
        return []
