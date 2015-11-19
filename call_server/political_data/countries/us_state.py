import csv
import collections
import random

from sunlight import openstates, response_cache
from . import DataProvider

from ...campaign.constants import (TARGET_CHAMBER_BOTH, TARGET_CHAMBER_UPPER, TARGET_CHAMBER_LOWER,
        ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)


class USStateData(DataProvider):
    KEY_OPENSTATES = 'us_state:openstates:{id}'
    KEY_GOVERNOR = 'us_state:governor:{state}'

    def __init__(self, cache, api_cache=None):
        self.cache = cache
        if api_cache:
            response_cache.enable(api_cache)

    def _load_governors(self):
        """
        Load US state governor data from saved file
        Returns a dictionary keyed by state to cache for fast lookup

        eg us:governor:CA = {'title':'Governor', 'name':'Jerry Brown Jr.', 'phone': '18008076755'}
        """
        governors = collections.defaultdict(list)

        with open('call_server/political_data/data/us_states.csv') as f:
            reader = csv.DictReader(f)

            for l in reader:
                direct_key = self.KEY_GOVERNOR.format(**l)
                d = {
                    'title': 'Governor',
                    'name': l.get('governor'),
                    'phone': l.get('phone_primary'),
                }
                governors[direct_key].append(d)

        return governors

    def load_data(self):
        governors = self._load_governors()

        if hasattr(self.cache, 'set_many'):
            self.cache.set_many(governors)
        elif hasattr(self.cache, 'update'):
            self.cache.update(governors)
        else:
            raise AttributeError('cache does not appear to be dict-like')

    def cache_set(self, key, val):
        if hasattr(self.cache, 'set'):
            self.cache.set(key, val)
        elif hasattr(self.cache, 'update'):
            self.cache.update({key: val})
        else:
            raise AttributeError('cache does not appear to be dict-like')

    def get_legid(self, legid):
        cache_key = self.KEY_OPENSTATES.format(id=legid)
        return self.get_key(cache_key)

    def get_uid(self, key):
        return self.cache.get(key)

    def get_governor(self, state):
        cache_key = self.KEY_GOVERNOR.format(state=state)
        return self.cache.get(cache_key, [{}])[0]

    def locate_targets(self, latlon, chambers=TARGET_CHAMBER_BOTH, order=ORDER_IN_ORDER, state=None):
        """ Find all state legistlators for a location, as comma delimited (lat,lon)
            Returns a list of cached openstate keys in specified order.
        """
        try:
            (lat, lon) = latlon.split(',')
        except ValueError:
            raise ValueError('USStateData requires location as lat,lon')

        legislators = openstates.legislator_geo_search(lat, lon)
        targets = []
        senators = []
        house_reps = []

        # save full legislator data to cache
        # just uids to result list
        for l in legislators:
            if not l['active']:
                # don't include inactive legislators
                continue

            if state and (state.upper() != l['state'].upper()):
                # limit to one state
                continue

            cache_key = self.KEY_OPENSTATES.format(**l)
            self.cache_set(cache_key, l)

            if l['chamber'] == 'upper':
                senators.append(cache_key)
            if l['chamber'] == 'lower':
                house_reps.append(cache_key)

        if chambers == TARGET_CHAMBER_UPPER:
            targets = senators
        elif chambers == TARGET_CHAMBER_LOWER:
            targets = house_reps
        else:
            # default to TARGET_CHAMBER_BOTH
            if order == ORDER_UPPER_FIRST:
                targets.extend(senators)
                targets.extend(house_reps)
            elif order == ORDER_LOWER_FIRST:
                targets.extend(house_reps)
                targets.extend(senators)
            else:
                # default to name
                targets.extend(senators)
                targets.extend(house_reps)
                targets.sort()

        if order == ORDER_SHUFFLE:
            random.shuffle(targets)

        return targets
