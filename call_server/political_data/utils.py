import csv
from ..political_data import us_districts, us_legislators


def load_us_legislators():
    """
    Load US legislator data from saved file
    """
    legislators = []

    with open('data/us_legislators.csv') as f:
        reader = csv.DictReader(f)

        for legislator in reader:
            if legislator['senate_class']:
                legislator['chamber'] = 'senate'
            else:
                legislator['chamber'] = 'house'

            legislators.append(legislator)

    legislators = [l for l in legislators if l['in_office'] == '1']
    return legislators


def load_us_districts():
    """
    Load US congress district data from saved file
    """
    districts = []

    with open('data/us_districts.csv') as f:
        reader = csv.DictReader(
            f, fieldnames=['zipcode', 'state', 'district_number'])

        for district in reader:
            districts.append(district)

    return districts


def locate_targets(zipcode):
    local_districts = [d for d in us_districts
                       if d['zipcode'] == str(zipcode)]

    states = [d['state'] for d in local_districts]
    senators = [l for l in us_legislators
                if l['chamber'] == 'senate'
                and l['state'] in states]

    district_numbers = [d['district_number'] for d in local_districts]
    reps = [l for l in us_legislators
            if l['chamber'] == 'house'
            and l['state'] in states
            and l['district'] in district_numbers]

    return {'senate': senators, 'house': reps}
