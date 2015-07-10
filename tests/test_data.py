from test import BaseTestCase
from call_server.political_data import cache, lookup


class TestData(BaseTestCase):
    def setUp(self):
        legislators = cache.load_us_legislators()
        districts = cache.load_us_districts()

        self.cache = legislators.copy()
        self.cache.update(districts)

    def test_cache(self):
        self.assertIsNotNone(self.cache)

    def test_districts(self):
        district = self.cache['us:zipcode:94612'][0]
        self.assertEqual(district['state'], 'CA')
        self.assertEqual(district['house_district'], '13')

    def test_district_multiple_states(self):
        district = self.cache['us:zipcode:53811']
        self.assertEqual(len(district), 4)

    def test_senate(self):
        senator = self.cache['us:senate:CA'][0]
        self.assertEqual(senator['chamber'], 'senate')
        self.assertEqual(senator['state'], 'CA')
        self.assertEqual(senator['in_office'], '1')

    def test_house(self):
        rep = self.cache['us:house:CA:13'][0]
        self.assertEqual(rep['chamber'], 'house')
        self.assertEqual(rep['state'], 'CA')
        self.assertEqual(rep['district'], '13')
        self.assertEqual(rep['in_office'], '1')

    def test_locate_member_ids(self):
        ids = lookup.locate_targets('98004', cache=self.cache)

        self.assertEqual(len(ids), 4)
        self.assertEqual(ids[0]['bioguide_id'], 'C000127')
