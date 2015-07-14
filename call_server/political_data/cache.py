import csv
import collections
from ..extensions import cache


def load_us_legislators():
    """
    Load US legislator data from saved file
    Returns a dictionary keyed by state to cache for fast lookup

    eg us:senate:CA = [{'title':'Sen', 'first_name':'Dianne',  'last_name': 'Feinstein', ...},
                       {'title':'Sen', 'first_name':'Barbara', 'last_name': 'Boxer', ...}]
    or us:house:CA:13 = [{'title':'Rep', 'first_name':'Barbara',  'last_name': 'Lee', ...}]
    """
    legislators = collections.defaultdict(list)

    with open('call_server/political_data/data/us_legislators.csv') as f:
        reader = csv.DictReader(f)

        for l in reader:
            if l['in_office'] != '1':
                # skip if out of office
                continue

            direct_key = 'us:bioguide:{0[bioguide_id]}'.format(l)
            legislators[direct_key].append(l)

            if l['senate_class']:
                l['chamber'] = 'senate'
                chamber_key = 'us:{0[chamber]}:{0[state]}'.format(l)
            else:
                l['chamber'] = 'house'
                chamber_key = 'us:{0[chamber]}:{0[state]}:{0[district]}'.format(l)
            legislators[chamber_key].append(l)

    return legislators


def load_us_districts():
    """
    Load US congressional district data from saved file
    Returns a dictionary keyed by zipcode to cache for fast lookup

    eg us:zipcode:94612 = [{'state':'CA', 'house_district': 13}]
    or us:zipcode:54409 = [{'state':'WI', 'house_district': 7}, {'state':'WI', 'house_district': 8}]
    """
    districts = collections.defaultdict(list)

    with open('call_server/political_data/data/us_districts.csv') as f:
        reader = csv.DictReader(
            f, fieldnames=['zipcode', 'state', 'house_district'])

        for d in reader:
            cache_key = 'us:zipcode:{0[zipcode]}'.format(d)
            districts[cache_key].append(d)

    return districts


def load_us_data():
    districts = load_us_districts()
    cache.set_many(districts)

    legislators = load_us_legislators()
    cache.set_many(legislators)
