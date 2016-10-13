# translate country specific data to campaign.target field names


def adapt_to_target(data, key_prefix):
    if key_prefix == "us:bioguide":
        adapter = UnitedStatesData()
        return adapter.adapt(data)
    elif key_prefix == "us_state:openstates":
        adapter = OpenStatesData()
        return adapter.adapt(data)
    elif key_prefix == "us_state:governor":
        adapter = GovernorAdapter()
        return adapter.adapt(data)
    else:
        return data
    # TODO add for other countries


class UnitedStatesData(object):
    def adapt(self, data):
        mapped = {}
        mapped['name'] = '{first_name} {last_name}'.format(**data)
        mapped['number'] = data['phone']
        mapped['title'] = data['title']
        mapped['uid'] = data['bioguide_id']

        return mapped


class OpenStatesData(object):
    def adapt(self, data):
        mapped = {}
        mapped['name'] = data['full_name']
        if data['chamber'] == "upper":
            mapped['title'] = "Senator"
        if data['chamber'] == "lower":
            mapped['title'] = "Representative"
        if type(data['offices']) == list and 'phone' in data['offices'][0]:
            mapped['number'] = data['offices'][0]['phone']
        elif type(data['offices']) == dict and 'phone' in data['offices']:
            mapped['number'] = data['offices']['phone']
        else:
            mapped['number'] = None
        mapped['uid'] = data['leg_id']

        return mapped


class GovernorAdapter(object):
    def adapt(self, data):
        mapped = {}
        mapped['name'] = '{first_name} {last_name}'.format(**data)
        mapped['title'] = data['title']
        mapped['number'] = data['phone']
        mapped['uid'] = data['state']
        return mapped
