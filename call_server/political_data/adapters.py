# translate country specific data to campaign.target field names


def adapt_to_target(data, key_prefix):
    if key_prefix == "us:bioguide":
        adapter = SunlightData()
        return adapter.adapt(data)
    elif key_prefix == "us_state:openstates":
        adapter = OpenStatesData()
        return adapter.adapt(data)
    else:
        return data
    # TODO add for other countries


class SunlightData(object):
    def adapt(self, data):
        mapped = {}
        mapped['name'] = '{firstname} {lastname}'.format(**data)
        if data['title'] == "Sen":
            mapped['title'] = "Senator"
        if data['title'] == "Rep":
            mapped['title'] = "Representative"
        mapped['number'] = data['phone']
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
        mapped['number'] = data['offices'][0]['phone']
        mapped['uid'] = data['leg_id']

        return mapped
