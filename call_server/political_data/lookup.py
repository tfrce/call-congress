from ..extensions import cache


def locate_targets(zipcode):
    local_districts = cache.get('us:zipcode:{0}'.format(zipcode))

    states = [d['state'] for d in local_districts]  # yes, there are zipcodes that cross states
    senators = [cache.get('us:senate:'+state) for state in states]

    district_numbers = [d['house_district'] for d in local_districts]
    reps = [l for l in cache.get('us:house:{0}'.format(state)) for state in states
            if l['district'] in district_numbers]

    targets = senators + reps
    return targets
