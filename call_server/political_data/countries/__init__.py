
class CountryData(object):
    def load_data(self):
        """ Load all country specific data from csv files, save to cache """
        raise NotImplementedError

    def locate_targets(self, location):
        """ Find all targets for a location, crossing political boundaries if necessary.
        Returns a list of target uids."""
        raise NotImplementedError
