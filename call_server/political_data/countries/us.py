import csv
import collections
from . import CountryData


class USData(CountryData):
    KEY_BIOGUIDE = 'us:bioguide:{bioguide_id}'
    KEY_HOUSE = 'us:house:{state}:{district}'
    KEY_SENATE = 'us:senate:{state}'
    KEY_ZIPCODE = 'us:zipcode:{zipcode}'

    def __init__(self, cache):
        self.cache = cache

    def _load_legislators(self):
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

                direct_key = self.KEY_BIOGUIDE.format(**l)
                legislators[direct_key].append(l)

                if l['senate_class']:
                    l['chamber'] = 'senate'
                    chamber_key = self.KEY_SENATE.format(**l)
                else:
                    l['chamber'] = 'house'
                    chamber_key = self.KEY_HOUSE.format(**l)
                legislators[chamber_key].append(l)

        return legislators

    def _load_districts(self):
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
                cache_key = self.KEY_ZIPCODE.format(**d)
                districts[cache_key].append(d)

        return districts

    def load_data(self):
        districts = self._load_districts()
        legislators = self._load_legislators()

        if hasattr(self.cache, 'set_many'):
            self.cache.set_many(districts)
            self.cache.set_many(legislators)
        elif hasattr(self.cache, 'update'):
            self.cache.update(legislators)
            self.cache.update(districts)
        else:
            raise AttributeError('cache does not appear to be dict-like')

    # convenience methods for easy house, senate, district access
    def get_house_member(self, state, district):
        key = self.KEY_HOUSE.format(state=state, district=district)
        return self.cache.get(key)

    def get_senators(self, state):
        return self.cache.get(self.KEY_SENATE.format(state=state))

    def get_district(self, zipcode):
        return self.cache.get(self.KEY_ZIPCODE.format(zipcode=zipcode))

    def get_uid(self, uid):
        return self.cache.get(self.KEY_BIOGUIDE.format(bioguide_id=uid))

    def locate_member_ids(self, zipcode, chambers, order):
        """ Find all congressional targets for a zipcode, crossing state boundaries if necessary.
        Returns a list of bioguide ids in specified order.
        """

        districts = self.cache.get(self.KEY_ZIPCODE.format(zipcode=zipcode))
        states = set(d['state'] for d in districts)  # yes, there are zipcodes that cross states
        if not states:
            return None

        targets = []
        for state in states:
            for senator in self.get_senators(state):
                targets.append(senator['bioguide_id'])
        for d in districts:
            rep = self.get_house_member(d['state'], d['house_district'])
            targets.append(rep[0]['bioguide_id'])

        return targets
