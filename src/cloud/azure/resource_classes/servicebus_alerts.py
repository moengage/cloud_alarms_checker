import copy
import requests
from cloud.azure.utils.utils import *

def get_servicebus_list():

    servicebus_query = f'resources | where type == "microsoft.servicebus/namespaces" | where resourceGroup == "{resource_group}" | project name'

    return get_resources_list(servicebus_query, dc=dc_map, get_full_properties=False)

def get_queue_list(servicebus_list):

    subscription_id = dc_map["subscription_id"]

    global servicebus_queue_map
    servicebus_queue_map = {}

    metric_details = {'NumberOfMessagesVisible': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}}

    headers = get_header()

    for servicebus in servicebus_list:

        get_query_url = f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ServiceBus/namespaces/{servicebus}/queues?api-version=2021-11-01'

        response = requests.get(get_query_url, headers=headers)

        while(True):

            response = requests.get(get_query_url, headers=headers)

            if response.status_code == 200:

                result = json.loads(response.content)

                for queue in  result['value']:
                    if servicebus not in servicebus_queue_map:
                        servicebus_queue_map[servicebus] = {}

                    servicebus_queue_map[servicebus][queue['name']] = copy.deepcopy(metric_details)

                if 'nextLink' not in result:
                    break
                else:
                    get_query_url = result['nextLink']

            elif response.status_code == 429:

                print("sleeping for 5 min as request throttled")
                time.sleep(5)
                get_servicebus_list()
                return

            else:

                print(response.content)
                print(response.status_code)
                sys.exit(1)

def get_queue_tags():

    queuetags_query = f'resources | where type == "microsoft.insights/autoscalesettings" | where resourceGroup == "prod" | project split(properties["targetResourceUri"], "/", 8)[0]  ,  properties["profiles"][0]["rules"]'

    queue_tags = get_resources_list(queuetags_query, dc=dc_map, get_full_properties=True)


    vmss_tags_query = f'resources | where type == "microsoft.compute/virtualmachinescalesets" | where resourceGroup == "prod" | project name, tags'
    vmss_tags = get_resources_list(vmss_tags_query, dc=dc_map, get_full_properties=True)


    vmss_tags_map = {}

    for vmss_name in vmss_tags:

        if vmss_name[0] not in vmss_tags_map:
            tags= [vmss_name[1].get('Business', ""), vmss_name[1].get('Service', ""), vmss_name[1].get('SubService', "")]
            vmss_tags_map[vmss_name[0]] = tags

    queue_tag_map = {}

    for queue_tag in queue_tags:

        for more_queue_tag in queue_tag[1]:

            if more_queue_tag['metricTrigger']['metricName'] == "ActiveMessages":

                for dimension in more_queue_tag['metricTrigger']['dimensions']:

                    for queue_name in dimension['Values']:

                        if queue_name not in queue_tag_map:
                            queue_tag_map[queue_name] = vmss_tags_map[queue_tag[0]]
    return queue_tag_map

def get_servicebus_metrics():

    servicebus_metrics_query = f'resources | where type == "microsoft.insights/metricalerts" | where properties["criteria"]["allOf"][0]["metricNamespace"] == "Microsoft.ServiceBus/namespaces" | where properties["criteria"]["allOf"][0]["metricName"] == "ActiveMessages" |  where resourceGroup == "{resource_group}" | project properties, name'

    return get_resources_list(servicebus_metrics_query, dc=dc_map, get_full_properties=True)


def  write_service_bus_metrics_to_spreadsheet( service_bus_sheet, servicebus_list, dc_name, table):

    servicebus_queue_tags = get_queue_tags()

    rows = []
    for servicebus_name in servicebus_list:
        for queue_name in servicebus_queue_map[servicebus_name]:

            if servicebus_queue_map[servicebus_name][queue_name] == {}:
                continue

            row = [dc_name, servicebus_name]

            msg = ''
            bp = servicebus_queue_map[servicebus_name][queue_name]
            for metric in bp:
                if bp[metric]['alarm_present'] == 'no':
                    msg = msg + f'{metric} --- Alarm Not Present \n'

                if bp[metric]['alarm_present'] == 'yes':
                    msg = msg + f'{metric} --- Action Group Is Missing for Alarm [{bp[metric]["link"]}]  \n'

            if queue_name in servicebus_queue_tags:
                row.extend([queue_name, servicebus_queue_tags[queue_name][0], servicebus_queue_tags[queue_name][1],  servicebus_queue_tags[queue_name][2] , msg])
            else:
                row.extend([queue_name,  "", "", "" , msg ])

            rows.append(row)

    service_bus_sheet.append_rows(rows, value_input_option='USER_ENTERED')

def get_servicebus_missing_metrics(service_bus_sheet, dc , dc_name , table):

    global dc_map
    dc_map = dc    

    global resource_group
    resource_group = dc["resource_group"]


    servicebus_list = get_servicebus_list()

    get_queue_list(servicebus_list)

    servicebus_metrics_list = get_servicebus_metrics()

    for alarm_metric in servicebus_metrics_list:

        alarm_metric_details = alarm_metric[0]
        alarm_name = alarm_metric[1]

        alarm_metric_dimensions = alarm_metric_details["criteria"]["allOf"][0]["dimensions"]

        service_bus_name = alarm_metric_details['scopes'][0].split('/')[-1]

        for dimension in alarm_metric_dimensions:
            if dimension['name'] == 'EntityName' and dimension['operator'] == 'Include' and len(dimension['values']) > 0:
                for queue_name in dimension['values']:
                    if len(alarm_metric_details['actions']) == 0 :
                        servicebus_queue_map[service_bus_name][queue_name]["NumberOfMessagesVisible"]["link"] = alarm_name
                        servicebus_queue_map[service_bus_name][queue_name]['NumberOfMessagesVisible']["alarm_present"] = "yes"
                    else:
                        del servicebus_queue_map[service_bus_name][queue_name]["NumberOfMessagesVisible"]

    write_service_bus_metrics_to_spreadsheet( service_bus_sheet, servicebus_list, dc_name, table)
