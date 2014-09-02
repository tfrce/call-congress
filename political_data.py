import csv
import yaml
import random
import time
import urllib2
import json

class PoliticalData():

    SPREADSHEET_CACHE_TIMEOUT = 4 # seconds

    overrides_data = {}
    cache_handler = None
    campaigns = None
    legislators = None
    districts = None
    debug_mode = False

    def __init__(self, cache_handler, debug_mode):
        """
        Load data in database
        """
        legislators = []

        self.cache_handler = cache_handler
        self.debug_mode = debug_mode

        with open('data/legislators.csv') as f:
            reader = csv.DictReader(f)

            for legislator in reader:
                if legislator['senate_class']:
                    legislator['chamber'] = 'senate'
                else:
                    legislator['chamber'] = 'house'

                legislators.append(legislator)

        legislators = [l for l in legislators if l['in_office'] == '1']

        districts = []

        with open('data/districts.csv') as f:
            reader = csv.DictReader(
                f, fieldnames=['zipcode', 'state', 'district_number'])

            for district in reader:
                districts.append(district)

        with open('data/campaigns.yaml', 'r') as f:
            campaigns = {c['id']: c for c in yaml.load(f.read())}

        self.campaigns = campaigns
        self.legislators = legislators
        self.districts = districts

    def get_campaign(self, campaign_id):
        if campaign_id in self.campaigns:
            return dict(self.campaigns['default'],
                        **self.campaigns[campaign_id])

    def get_senators(self, districts):
        states = [d['state'] for d in districts]

        senators = [l for l in self.legislators
                if l['chamber'] == 'senate'
                and l['state'] in states]

        random.shuffle(senators)    # mix it up! always do this :)

        return senators

    def get_house_members(self, districts):
        states = [d['state'] for d in districts]
        district_numbers = [d['district_number'] for d in districts]

        return [l for l in self.legislators
                if l['chamber'] == 'house'
                and l['state'] in states
                and l['district'] in district_numbers]

    def locate_member_ids(self, zipcode, campaign):
        """get congressional member ids from zip codes to districts data"""
        local_districts = [d for d in self.districts
                           if d['zipcode'] == str(zipcode)]
        member_ids = []

        individual_target = campaign.get('target_member_id', None)

        if individual_target:
            member_ids = [individual_target]
            return member_ids

        target_senate = campaign.get('target_senate')
        target_house_first = campaign.get('target_house_first')
        target_house = campaign.get('target_house')

        # Instantiate some extra variables related to state-specific overrides
        target_individual = None
        state = None
        first_call_name = None
        first_call_number = None

        # check if there's a google spreadsheet with state-specific overrides
        if self.has_special_overrides(local_districts, campaign):

            overrides = self.get_override_values(local_districts, campaign)

            target_senate = overrides['target_senate']
            target_house_first = overrides['target_house_first']
            target_house = overrides['target_house']
            target_individual = overrides['target_individual']
            first_call_name = overrides['first_call_name']
            first_call_number = overrides['first_call_number']
            state = overrides['_STATE_ABBREV']

        # filter list by campaign target_house, target_senate
        if target_senate and not target_house_first:
            member_ids.extend([s['bioguide_id']
                               for s in self.get_senators(local_districts)])

        if target_house:
            member_ids.extend([h['bioguide_id'] for h
                               in self.get_house_members(local_districts)])

        if target_senate and target_house_first:
            member_ids.extend([s['bioguide_id']
                               for s in self.get_senators(local_districts)])

        if campaign.get('randomize_order', False):
            random.shuffle(member_ids)

        # if targeting an individual by name, pop them to the front of the list
        # JL NOTE ~ Tony C=>A<=rdenas (C001097) has bad data, unicode warning
        if target_individual != None and target_individual != "":
            for l in self.legislators:
                if l['lastname'] == target_individual and l['state'] == state:
                    if l['bioguide_id'] in member_ids:
                            member_ids.remove(l['bioguide_id'])     # janky
                            member_ids.insert(0, l['bioguide_id'])  # lol

        # Finally, for some states we want to call a special name/number first.
        # We are going to shoehorn this data into the existing member_ids
        # paradigm and specially parse it. Super janky, but c'est la vie.
        if first_call_number and first_call_name:
            shoehorned_data = "SPECIAL_CALL_%s" % json.dumps({
                'name': first_call_name, 'number': first_call_number})
            member_ids.insert(0, shoehorned_data)

        return member_ids

    def get_override_values(self, local_districts, campaign):

        overrides = self.get_overrides(campaign)

        states = [d['state'] for d in local_districts]

        for state in states:
            override = overrides.get(state)
            if override:
                override['_STATE_ABBREV'] = state
                if self.debug_mode:
                    print "Found overrides: %s / %s" % (state, str(override))
                return overrides.get(state)

        return None

    def has_special_overrides(self, local_districts, campaign):

        spreadsheet_id = campaign.get('overrides_google_spreadsheet_id', None)

        if spreadsheet_id == None:
            return False

        overrides = self.get_overrides(campaign)

        states = [d['state'] for d in local_districts]

        for state in states:
            if overrides.get(state):
                return True

        return False

    def get_overrides(self, campaign):

        if self.overrides_data.get(campaign.get('id')) == None:
            self.populate_overrides(campaign)

        return self.overrides_data[campaign.get('id')]

    def populate_overrides(self, campaign):

        spreadsheet_id = campaign.get('overrides_google_spreadsheet_id', None)
        spreadsheet_key = '%s-spreadsheet-data' % campaign.get('id')
        
        overrides_data = self.cache_handler.get(spreadsheet_key, None)
        
        if overrides_data == None:
            overrides = self.grab_overrides_from_google(spreadsheet_id)
            if self.debug_mode:
                print "GOT DATA FROM GOOGLE: %s" % str(overrides)

            self.cache_handler.set(
                spreadsheet_key,
                json.dumps(overrides),
                self.SPREADSHEET_CACHE_TIMEOUT)
        else:
            overrides = json.loads(overrides_data)
            if self.debug_mode:
                print "GOT DATA FROM CACHE: %s" % str(overrides)
        
        self.overrides_data[campaign.get('id')] = overrides

    def grab_overrides_from_google(self, spreadsheet_id):

        url = ('https://spreadsheets.google.com/feeds/list/'
                '%s/default/public/values?alt=json') % spreadsheet_id

        response = urllib2.urlopen(url).read()
        data = json.loads(response)

        def is_true(val):
            return True if val == "TRUE" else False

        overrides = {}
        
        for row in data['feed']['entry']:

            state = row['gsx$state']['$t']
            target_senate = is_true(row['gsx$targetsenate']['$t'])
            target_house = is_true(row['gsx$targethouse']['$t'])
            target_house_first = is_true(row['gsx$targethousefirst']['$t'])
            individual = row['gsx$optionaltargetindividualfirstlastname']['$t']
            first_call_name = row['gsx$optionalextrafirstcallname']['$t']
            first_call_number = row['gsx$optionalextrafirstcallnumber']['$t']

            overrides[state] = {
                'target_senate': target_senate,
                'target_house': target_house,
                'target_house_first': target_house_first,
                'target_individual': individual,
                'first_call_name': first_call_name,
                'first_call_number': first_call_number
            }

        return overrides

