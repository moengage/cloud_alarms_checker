from cloud.azure.resource_classes.backendpool_alerts import get_backendpool_missing_metrics
from cloud.azure.resource_classes.servicebus_alerts import get_servicebus_missing_metrics
from cloud.azure.resource_classes.redis_alerts import get_redis_missing_metrics
from cloud.azure.resource_classes.action_group import get_invalid_action_group

from cloud.azure.utils.utils import *

def azure_alarm_checker(env, yaml_inputs,spreadsheet_writer):

    # spreadsheet_writer = get_spreadheet(env)
    ENV_REGION_MAP = yaml_inputs['env_region_map']

    backend_pool_header_row = ['Dc Name', 'Gateway Name' , 'Backend Pool Name', 'Business', 'Service', 'SubService', 'Missing Alarm Metrics With Reason' ]
    backend_pool_sheet = spreadsheet_writer.create_sheet('Backend Pool', backend_pool_header_row)

    servicebus_header_row = ['Dc Name', 'Service Bus Name' , 'Queue Name', 'Business', 'Service', 'SubService', 'Missing Alarm Metrics With Reason' ]
    servicebus_sheet = spreadsheet_writer.create_sheet('Service Bus', servicebus_header_row)

    redis_header_row = ['Dc Name', 'Redis Name' , 'Business', 'Service', 'SubService', 'Missing Alarm Metrics With Reason' ]
    redis_sheet = spreadsheet_writer.create_sheet('Redis', redis_header_row)

    actiongroup_header_row = ['Dc Name', 'Action Group  Name' , 'Business', 'Team', 'Reason' ]
    action_group_sheet = spreadsheet_writer.create_sheet('Action Group', actiongroup_header_row)

    for dc in ENV_REGION_MAP:
        
        set_header(ENV_REGION_MAP[dc])

        print(f"Fetching for Backend Pool Metrics in {dc}")
        get_backendpool_missing_metrics(backend_pool_sheet, ENV_REGION_MAP[dc], dc, 'backend_pool_table')

        print(f"Fetching for Service Bus Metrics in {dc}")
        get_servicebus_missing_metrics(servicebus_sheet, ENV_REGION_MAP[dc], dc, "servicebus_table")

        print(f"Fetching for redis Metrics in {dc}")
        get_redis_missing_metrics(redis_sheet, ENV_REGION_MAP[dc], dc, "redis_table")

        print(f"Fetching for Invalid Action Group in {dc}")
        get_invalid_action_group(action_group_sheet, ENV_REGION_MAP[dc], dc, "action_group_table")
        
    return True