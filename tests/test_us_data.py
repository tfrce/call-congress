from test import BaseTestCase
from call_server.political_data.countries.us import USData
from call_server.campaign.constants import (
    ORDER_IN_ORDER, ORDER_SHUFFLE, ORDER_SENATE_FIRST, ORDER_HOUSE_FIRST)


class TestData(BaseTestCase):
    def setUp(self):
        # mock the flask-cache as a dictionary
        dictCache = {}
        self.us_data = USData(dictCache)

    def test_cache(self):
        self.assertIsNotNone(self.cache)

    def test_districts(self):
        district = self.us_data.get_district('94612')[0]
        self.assertEqual(district['state'], 'CA')
        self.assertEqual(district['house_district'], '13')

    def test_district_multiple_states(self):
        districts = self.us_data.get_district('53811')
        # apparently this zipcode is in multiple states
        self.assertEqual(len(districts), 4)

    def test_senate(self):
        senator = self.us_data.get_senators('CA')[0]
        self.assertEqual(senator['chamber'], 'senate')
        self.assertEqual(senator['state'], 'CA')
        self.assertEqual(senator['in_office'], '1')

    def test_house(self):
        rep = self.us_data.get_house_member('CA', '13')[0]
        self.assertEqual(rep['chamber'], 'house')
        self.assertEqual(rep['state'], 'CA')
        self.assertEqual(rep['district'], '13')
        self.assertEqual(rep['in_office'], '1')

    def test_get_targets(self):
        uids = self.us_data.locate_member_ids('05055', ORDER_IN_ORDER)
        # returns a list of bioguide ids
        self.assertEqual(len(uids), 3)

        senator_0 = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(senator_0['chamber'], 'senate')
        self.assertEqual(senator_0['state'], 'VT')
        self.assertEqual(senator_0['in_office'], '1')

        senator_1 = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(senator_1['chamber'], 'senate')
        self.assertEqual(senator_1['state'], 'VT')
        self.assertEqual(senator_1['in_office'], '1')

        house_rep = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(house_rep['chamber'], 'house')
        self.assertEqual(house_rep['state'], 'VT')
        self.assertEqual(house_rep['in_office'], '1')
