import requests

def get_business_team_map(inputs):

    '''
        Fetch the business team map from Consul Host
    '''
    if inputs['consul']['useConsul'] == True:

        url = (
            '{host}/v1/kv/confd-configs/kvs/maps/business_team_map.json?raw'.format(  # noqa: E501
                host=inputs['consul']['url']))

        print('Getting buisness team map config from %s' % url)

        r = requests.get(url)
        return r.json()