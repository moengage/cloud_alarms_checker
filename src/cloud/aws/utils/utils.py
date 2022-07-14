from collections import defaultdict
from cloud.aws.utils.constants import (ResourceType)

def get_resource_name_from_dimensions(resource_type, dimensions):

    '''
        This will fetch the resource name from the list of dimensions fetched from the get_metric_data response
    '''

    resource_name = ''

    for dimension in dimensions:

        # If dimension name is equal to one of the resource for which alarms are fetched, then it is selected
        if dimension["Name"] == resource_type:
            resource_name = dimension["Value"]

            # In case of LOAD_BALANCER and TARGET_GROUP, resource name will be the seconf index
            if resource_type in [ResourceType.LOAD_BALANCER, ResourceType.TARGET_GROUP]:  # noqa: E501
                resource_name = resource_name.split("/")[1]

            break

    return resource_name


def get_alarm_link(alarm_name, region):

    '''
        Given the region and alarm name, return the AWS cloudwatch console link of the alarm.

    '''

    return "https://console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{alarm_name}".format(  # noqa: E501
        region=region, alarm_name='+'.join(alarm_name.split(' ')))


def group_alarms_by_resource(resource_type_alarm_action_map):
    
    resource_group = defaultdict(dict)

    for resource_type, alarms in resource_type_alarm_action_map.items():
        for alarm in alarms:
            resource_name = alarm[0]
            alarm_actions = alarm[3]

            if resource_name not in resource_group[resource_type]:
                resource_group[resource_type][resource_name] = set()

            resource_group[resource_type][resource_name].update(alarm_actions)

    return resource_group

def get_region_from_arn(arn):
    return arn.split(":")[3]