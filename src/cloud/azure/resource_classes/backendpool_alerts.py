import copy
from cloud.azure.utils.utils import *

def get_gateway_list():
    application_gateway_query = f'resources | where type == "microsoft.network/applicationgateways" |  where resourceGroup == "{resource_group}" |  project name' 

    return get_resources_list(application_gateway_query, dc=dc_map)

def get_backendpool_list(gateway_list):


    metric_details = {'Http4xxCount': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}, 'Http5xxCount': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}, 'TargetResponseTime-Avg': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}, 'HealthyHostCount': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}}

    global gateway_backend_pool 
    gateway_backend_pool = {}
    for gateway_name in gateway_list:

        backend_pool_query = f'resources | where type == "microsoft.network/applicationgateways" | where name == "{gateway_name}" | mv-expand properties.backendAddressPools |  where resourceGroup == "{resource_group}" | project properties_backendAddressPools["name"]'

        backend_pool_list = get_resources_list(backend_pool_query, dc=dc_map)

        for backend_pool in  backend_pool_list:
            if gateway_name not in gateway_backend_pool:
                gateway_backend_pool[gateway_name] = {}

            gateway_backend_pool[gateway_name][backend_pool] = copy.deepcopy(metric_details)

def get_backend_pool_metrics():
    backend_pool_metrics_query = f'resources | where type == "microsoft.insights/metricalerts" | where properties["criteria"]["allOf"][0]["metricNamespace"] == "Microsoft.Network/applicationGateways" | where properties["criteria"]["allOf"][0]["dimensions"][0]["name"] == "BackendPool" or properties["criteria"]["allOf"][0]["dimensions"][0]["name"] == "BackendSettingsPool" |  where resourceGroup == "{resource_group}" | project properties, name '

    return get_resources_list(backend_pool_metrics_query, dc=dc_map, get_full_properties=True)

def get_vmss_tags_for_bp():
    query = 'resources | where type == "microsoft.compute/virtualmachinescalesets" | where properties["virtualMachineProfile"]["networkProfile"]["networkInterfaceConfigurations"][0]["properties"]["ipConfigurations"][0]["properties"]["applicationGatewayBackendAddressPools"] != ""  | project properties["virtualMachineProfile"]["networkProfile"]["networkInterfaceConfigurations"][0]["properties"]["ipConfigurations"][0]["properties"]["applicationGatewayBackendAddressPools"], tags'

    bp_list = get_resources_list(query, dc=dc_map, get_full_properties=True)

    backend_pool_tags = {}

    for bp in bp_list:

        bp_names = [ elem['id'].split('/')[-1] for elem in bp[0] ]
        tags = [bp[1].get('Business', ""), bp[1].get('Service', ""), bp[1].get('SubService', "")]
        for bp_name in bp_names:
            backend_pool_tags[bp_name] = tags

    return backend_pool_tags

def get_host_count_metrics(bp_name, metric_name, alarm_name, alarm_metric_details, alarm_metric_dimensions, gateway_name ):
    if len(alarm_metric_dimensions[0]['values']) == 1:
        bp_name = alarm_metric_dimensions[0]['values'][0].split('~')[0]

    metric_name = alarm_metric_details["criteria"]["allOf"][0]["metricName"]


    if metric_name  in gateway_backend_pool[gateway_name][bp_name]: 
        if len(alarm_metric_details['actions']) == 0 :
            gateway_backend_pool[gateway_name][bp_name][metric_name]["link"] = alarm_name
            gateway_backend_pool[gateway_name][bp_name][metric_name]["alarm_present"] = "yes"
        else:
            del gateway_backend_pool[gateway_name][bp_name][metric_name]
    else:
        return

def get_response_time_metrics(bp_name, metric_name, alarm_name, alarm_metric_details, alarm_metric_dimensions, gateway_name ):
    if len(alarm_metric_dimensions[0]['values']) == 1:
        bp_name = alarm_metric_dimensions[0]['values'][0].split('~')[0]

    metric_name = alarm_metric_details["criteria"]["allOf"][0]["metricName"]
    if metric_name == 'BackendLastByteResponseTime':
        metric_name = "TargetResponseTime-Avg"

    else:
        return

    if   metric_name  in gateway_backend_pool[gateway_name][bp_name]: 
        if len(alarm_metric_details['actions']) == 0 :
            gateway_backend_pool[gateway_name][bp_name][metric_name]["link"] = alarm_name
            gateway_backend_pool[gateway_name][bp_name][metric_name]["alarm_present"] = "yes"

        else:

            del gateway_backend_pool[gateway_name][bp_name][metric_name]
    else:
        return

def get_status_code_metrics(bp_name, metric_name, alarm_name, alarm_metric_details, alarm_metric_dimensions, gateway_name ):
    for alarm_metric_dimension in alarm_metric_dimensions:

        if alarm_metric_dimension['name'] == "BackendPool":
            bp_name = alarm_metric_dimension['values'][0]

        if alarm_metric_dimension['name'] == "HttpStatusGroup":

            if len(alarm_metric_dimensions[0]['values']) == 1:
                metric_name = alarm_metric_dimension['values'][0]
                if metric_name == "4xx":
                    metric_name = "Http4xxCount"
                if metric_name == "5xx":
                    metric_name = "Http5xxCount"

        if bp_name != None and metric_name != None:
            if  metric_name  in gateway_backend_pool[gateway_name][bp_name]: 
                if len(alarm_metric_details['actions']) == 0 :
                    gateway_backend_pool[gateway_name][bp_name][metric_name]["link"] = alarm_name
                    gateway_backend_pool[gateway_name][bp_name][metric_name]["alarm_present"] = "yes"
                else:
                    del gateway_backend_pool[gateway_name][bp_name][metric_name]


def write_backend_pool_metrics_to_spreadsheet( backend_pool_sheet, gateway_list, dc_name, table):

    backend_pool_tags = get_vmss_tags_for_bp()

    rows = []
    for gateway_name in gateway_list:
        for backend_pool in gateway_backend_pool[gateway_name]:

            if gateway_backend_pool[gateway_name][backend_pool] == {}:
                continue

            row = [dc_name, gateway_name]

            msg = ''
            bp = gateway_backend_pool[gateway_name][backend_pool]
            for metric in bp:
                if bp[metric]['alarm_present'] == 'no':
                    # msg = msg + f'{metric} --- Alarm Not Present \n'
                    msg = msg + f'{metric}  --- Alarm Not Present \n'

                if bp[metric]['alarm_present'] == 'yes':
                    msg = msg + f'{metric} --- Action Group Is Missing for Alarm [{bp[metric]["link"]}]  \n'

            if backend_pool in backend_pool_tags:
                row.extend([backend_pool, backend_pool_tags[backend_pool][0], backend_pool_tags[backend_pool][1],  backend_pool_tags[backend_pool][2] , msg])
            else:
                row.extend([backend_pool,  "", "", "" , msg ])

            rows.append(row)

    backend_pool_sheet.append_rows(rows, value_input_option='USER_ENTERED')


def get_backendpool_missing_metrics( backend_pool_sheet, dc , dc_name , table):

    global dc_map
    dc_map = dc    

    global resource_group
    resource_group = dc["resource_group"]
    gateway_list = get_gateway_list()

    get_backendpool_list(gateway_list)

    backendpool_metrics_list = get_backend_pool_metrics()

    for alarm_metric in backendpool_metrics_list:

        bp_name = None
        metric_name = None
        alarm_name = alarm_metric[1]
        alarm_metric_details = alarm_metric[0]

        alarm_metric_dimensions = alarm_metric_details["criteria"]["allOf"][0]["dimensions"]
        gateway_name = alarm_metric_details["scopes"][0].split('/')[-1]


        if len(alarm_metric_dimensions) == 1:


            if alarm_metric_dimensions[0]['name'] == "BackendSettingsPool":
                get_host_count_metrics(bp_name, metric_name, alarm_name, alarm_metric_details, alarm_metric_dimensions, gateway_name )

            elif alarm_metric_dimensions[0]['name'] == "BackendPool":

                get_response_time_metrics(bp_name, metric_name, alarm_name, alarm_metric_details, alarm_metric_dimensions, gateway_name )
        else:
            get_status_code_metrics(bp_name, metric_name, alarm_name, alarm_metric_details, alarm_metric_dimensions, gateway_name )


    write_backend_pool_metrics_to_spreadsheet( backend_pool_sheet, gateway_list, dc_name, table)
