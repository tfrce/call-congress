# translate country specific data to campaign.target field names


def adapt_to_target(data, key_prefix):
    if key_prefix == "us:bioguide":
        adapter = SunlightData()
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
