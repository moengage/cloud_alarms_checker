import copy
import requests
from cloud.azure.utils.utils import *


def get_redis_list(dc_name):

    redis_query = f'resources | where type == "microsoft.cache/redis" | where resourceGroup  == "{resource_group}" | project name, tags'

    return get_resources_list(redis_query, dc=dc_map, get_full_properties=True)

def get_redis_metrics():

    redis_metrics_query = f'resources | where type == "microsoft.insights/metricalerts" | where properties["criteria"]["allOf"][0]["metricNamespace"] == "Microsoft.Cache/Redis" | project properties, name'

    return get_resources_list(redis_metrics_query, dc=dc_map, get_full_properties=True)


def  write_redis_metrics_to_spreadsheet( redis_sheet, redis_list, redis_tag_map, dc_name, table):

    rows = []
    for redis_name in redis_list:

            if redis_map[redis_name] == {}:
                continue

            row = [dc_name, redis_name]

            msg = ''
            bp = redis_map[redis_name]
            for metric in bp:
                if bp[metric]['alarm_present'] == 'no':
                    msg = msg + f'{metric} --- Alarm Not Present \n'

                if bp[metric]['alarm_present'] == 'yes': 
                    msg = msg + f'{metric} --- Action Group Is Missing for Alarm [{bp[metric]["link"]}]  \n'

            if redis_name in redis_tag_map:
                row.extend([redis_tag_map[redis_name][0], redis_tag_map[redis_name][1],  redis_tag_map[redis_name][2] , msg])
            else:
                row.extend([redis_name,  "", "", "" , msg ])

            rows.append(row)

    redis_sheet.append_rows(rows, value_input_option='USER_ENTERED')

def get_redis_missing_metrics(redis_sheet, dc , dc_name , table):

    global dc_map
    dc_map = dc    

    global resource_group
    resource_group = dc["resource_group"]


    redis_name_tags_list = get_redis_list(dc_name)


    redis_list = []
    redis_tag_map = {}

    global redis_map
    redis_map = {}

    for redis_name in redis_name_tags_list:
        redis_list.append(redis_name[0]) 

        metric_details = {'UsedMemoryPercentageInstanceBased': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}, 'CPUPercentageInstanceBased': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}, 'ServerLoadInstanceBased': {'action_group_present': 'false', 'link': '', 'alarm_present': 'no'}}

        if redis_name[0] not in redis_map:
            redis_map[redis_name[0]] = {}

        redis_map[redis_name[0]] = copy.deepcopy(metric_details)

        tags= [redis_name[1].get('Business', ""), redis_name[1].get('Service', ""), redis_name[1].get('SubService', "")]
        redis_tag_map[redis_name[0]] = tags

    redis_metrics_list = get_redis_metrics()


    for alarm_metric in redis_metrics_list:
        metric_name = None

        alarm_metric_details = alarm_metric[0]

        alarm_name = alarm_metric[1]

        alarm_metric_dimensions = alarm_metric_details["criteria"]["allOf"][0]["dimensions"]

        redis_name = alarm_metric_details['scopes'][0].split('/')[-1]

        if alarm_metric_details["criteria"]["allOf"][0]["metricName"] == "allpercentprocessortime":
            metric_name = "CPUPercentageInstanceBased"
        
        elif alarm_metric_details["criteria"]["allOf"][0]["metricName"] == "allserverLoad":
            metric_name = "ServerLoadInstanceBased"
            
        elif alarm_metric_details["criteria"]["allOf"][0]["metricName"] == "allusedmemorypercentage":
            metric_name = "UsedMemoryPercentageInstanceBased"

        if metric_name == None:
            continue
        for dimension in alarm_metric_dimensions:
            if dimension['name'] == 'ShardId' and dimension['operator'] == 'Include' and len(dimension['values']) > 0:
                if len(alarm_metric_details['actions']) == 0 :
                    redis_map[redis_name][metric_name]["link"] = alarm_name
                    redis_map[redis_name][metric_name]["alarm_present"] = "yes"
                else:
                    del redis_map[redis_name][metric_name]

    write_redis_metrics_to_spreadsheet( redis_sheet, redis_list, redis_tag_map, dc_name, table)