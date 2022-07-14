import datetime
import yaml
from yaml.loader import SafeLoader

def get_chunked_list(_list, chunk_size):

    '''
        Return a list of lists splitted by `chunk_size`.
    '''

    chunked_list = []
    chunk = []

    for item in _list:
        chunk.append(item)

        if len(chunk) == chunk_size:
            chunked_list.append(chunk)
            chunk = []

    if chunk:
        chunked_list.append(chunk)

    return chunked_list


def datetime_serializer(o):

    '''
        Date Time Serializer
    '''

    if isinstance(o, datetime.datetime):
        return o.__str__()


def yaml_reader(input):

    with open(input) as f:
        data = yaml.load(f, Loader=SafeLoader)
        return data['spec']