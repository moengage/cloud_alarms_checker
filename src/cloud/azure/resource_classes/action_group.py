from cloud.azure.utils.utils import *


def get_action_list():

    redis_query = f'resources | where type == "microsoft.insights/actiongroups" | where resourceGroup == "{resource_group}" | where properties["webhookReceivers"][0]["serviceUri"] == "" | project name, tags'

    return get_resources_list(redis_query, dc=dc_map, get_full_properties=True)

def get_invalid_action_group(action_group_sheet, dc , dc_name , table):

    global dc_map
    dc_map = dc    

    global resource_group
    resource_group = dc["resource_group"]


    action_group_list = get_action_list()

    print(action_group_list)

    rows = []
    for action_group in action_group_list:
        msg = "Pagerduty Endpoint Not Present"
        if action_group[1] != None:
            row = [dc_name, action_group[0]]
            row.extend([action_group[1].get("Business",""), action_group[1].get("Team","") , msg])
            rows.append(row)

    action_group_sheet.append_rows(rows, value_input_option='USER_ENTERED')
