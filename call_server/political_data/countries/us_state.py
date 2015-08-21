import random

from sunlight import openstates, response_cache
from . import DataProvider

from ...campaign.constants import (TARGET_CHAMBER_BOTH, TARGET_CHAMBER_UPPER, TARGET_CHAMBER_LOWER,
        ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)


class USStateData(DataProvider):
    KEY_OPENSTATES = 'us_state:openstates:{id}'

    def __init__(self, cache, api_cache=None):
        self.cache = cache
        if api_cache:
            response_cache.enable(api_cache)

    def load_data(self):
        "Not needed, data provided over Sunlight OpenStates API, and cached on response"
        pass

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

    def locate_targets(self, latlon, chambers=TARGET_CHAMBER_BOTH, order=ORDER_IN_ORDER):
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
