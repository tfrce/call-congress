from geocodio import GeocodioClient
import os

# light wrapper around geocode.io client
# with convenience properties to hide address components
# TODO, add non-US postal endpoints


class Location(dict):
    @property
    def state(self):
        return self.get('address_components', {}).get('state')

    @property
    def location(self):
        lat = self.get('location', {}).get('lat')
        lon = self.get('location', {}).get('lng')
        return (lat, lon)


class Geocoder(object):
    def __init__(self, API_KEY=None):
        if not API_KEY:
            # get keys from os.environ, because we may not have current_app context
            API_KEY = os.environ.get('GEOCODE_API_KEY')
        self.client = GeocodioClient(API_KEY)

    def geocode(self, address):
        results = self.client.geocode(address).get('results')
        if not results:
            return None
        else:
            return Location(results[0])

    def reverse(self, latlon):
        results = self.client.reverse(latlon).get('results')
        if not results:
            return None
        else:
            return Location(results[0])
