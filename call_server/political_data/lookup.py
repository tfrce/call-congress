from ..extensions import cache


def locate_targets(zipcode, cache=cache):
    local_districts = cache.get('us:zipcode:{0}'.format(zipcode))
    targets = []

    states = set(d['state'] for d in local_districts)  # yes, there are zipcodes that cross states
    for state in states:
        targets.extend(cache.get('us:senate:'+state))

    for d in local_districts:
        r = cache.get('us:house:{0[state]}:{0[house_district]}'.format(d))
        targets.extend(r)

    return targets
