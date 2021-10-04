from run import BaseTestCase
from call_server.political_data.countries.us import USData
from call_server.campaign.constants import (TARGET_CHAMBER_BOTH, TARGET_CHAMBER_UPPER, TARGET_CHAMBER_LOWER,
        ORDER_IN_ORDER, ORDER_UPPER_FIRST, ORDER_LOWER_FIRST)


class TestData(BaseTestCase):
    def setUp(self):
        # mock the flask-cache as a dictionary
        testCache = {}
        self.us_data = USData(testCache)
        self.us_data.load_data()

    def test_cache(self):
        self.assertIsNotNone(self.us_data)

    def test_districts(self):
        district = self.us_data.get_district('94612')[0]
        self.assertEqual(district['state'], 'CA')
        self.assertEqual(district['house_district'], '13')

    def test_district_multiple_states(self):
        districts = self.us_data.get_district('42223')
        # as of 09/27/2021 this zipcode is in multiple states (KY & TN)
        self.assertEqual(len(districts), 2)

    def test_senate(self):
        senator = self.us_data.get_senators('CA')[0]
        self.assertEqual(senator['chamber'], 'senate')
        self.assertEqual(senator['state'], 'CA')

    def test_house(self):
        rep = self.us_data.get_house_member('CA', '13')[0]
        self.assertEqual(rep['chamber'], 'house')
        self.assertEqual(rep['state'], 'CA')
        self.assertEqual(rep['district'], '13')

    def test_dc(self):
        no_senators = self.us_data.get_senators('DC')
        self.assertEqual(no_senators, [])

        rep = self.us_data.get_house_member('DC', '0')[0]
        self.assertEqual(rep['chamber'], 'house')
        self.assertEqual(rep['state'], 'DC')
        self.assertEqual(rep['district'], '0')

    def test_locate_targets(self):
        uids = self.us_data.locate_targets('05055', TARGET_CHAMBER_BOTH, ORDER_IN_ORDER)
        # returns a list of bioguide ids
        self.assertEqual(len(uids), 3)

        senator_0 = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(senator_0['chamber'], 'senate')
        self.assertEqual(senator_0['state'], 'VT')

        senator_1 = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(senator_1['chamber'], 'senate')
        self.assertEqual(senator_1['state'], 'VT')

        house_rep = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(house_rep['chamber'], 'house')
        self.assertEqual(house_rep['state'], 'VT')

    def locate_targets_house_only(self):
        uids = self.us_data.locate_targets('05055', TARGET_CHAMBER_LOWER)
        self.assertEqual(len(uids), 1)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'house')

    def locate_targets_senate_only(self):
        uids = self.us_data.locate_targets('05055', TARGET_CHAMBER_UPPER)
        self.assertEqual(len(uids), 2)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'senate')

        second = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(second['chamber'], 'senate')

    def test_locate_targets_ordered_house_first(self):
        uids = self.us_data.locate_targets('05055', TARGET_CHAMBER_BOTH, ORDER_LOWER_FIRST)
        self.assertEqual(len(uids), 3)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'house')

        second = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(second['chamber'], 'senate')

        third = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(third['chamber'], 'senate')

    def test_locate_targets_ordered_senate_first(self):
        uids = self.us_data.locate_targets('05055', TARGET_CHAMBER_BOTH, ORDER_UPPER_FIRST)
        self.assertEqual(len(uids), 3)

        first = self.us_data.get_uid(uids[0])[0]
        self.assertEqual(first['chamber'], 'senate')

        second = self.us_data.get_uid(uids[1])[0]
        self.assertEqual(second['chamber'], 'senate')

        third = self.us_data.get_uid(uids[2])[0]
        self.assertEqual(third['chamber'], 'house')
