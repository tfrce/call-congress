from ..extensions import cache
from ..campaign.constants import LOCATION_POSTAL, LOCATION_LATLNG


def locate_targets(parameter, segment_by=LOCATION_POSTAL, cache=cache):
    if segment_by is LOCATION_POSTAL:
        return locate_targets_by_zipcode(parameter, cache)
    # elif segment_by is LOCATION_LATLNG:
    #    TODO lookup target from latlng
    #    return locate_targets_by_latlng(parameter, cache)


def locate_targets_by_zipcode(zipcode, cache=cache):
    """ Locates all targets for a zipcode, crossing state boundaries if necessary.
    Returns a list of bioguide ids.
    """

    local_districts = cache.get('us:zipcode:{0}'.format(zipcode))
    states = set(d['state'] for d in local_districts)  # yes, there are zipcodes that cross states
    if not states:
        return None

    targets = []
    for state in states:
        for senator in cache.get('us:senate:' + state):
            targets.append(senator['bioguide_id'])
    for d in local_districts:
        rep = cache.get('us:house:{0[state]}:{0[house_district]}'.format(d))
        targets.append(rep[0]['bioguide_id'])

    return targets


def adapt_sunlight(data):
    mapped = {}
    mapped['name'] = '{firstname} {lastname}'.format(**data)
    if data['title'] == "Sen":
        mapped['title'] = "Senator"
    if data['title'] == "Rep":
        mapped['title'] = "Representative"
    mapped['number'] = data['phone']
    mapped['uid'] = data['bioguide_id']

    return mapped


def adapt_to_target(data, key_prefix):
    if key_prefix == "us:bioguide":
        return adapt_sunlight(data)
    else:
        return {}
    # TODO add for other countries
