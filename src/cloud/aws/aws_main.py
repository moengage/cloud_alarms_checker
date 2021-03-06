from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.team_map import *
from utils.utils import *
from prettytable import PrettyTable

from outputs.writer import *

from cloud.aws.utils.constants import MANDATORY_ALARM_METRICS
from cloud.aws.utils.utils import *
from cloud.aws.utils.alarms import *
from cloud.aws.utils.boto_client import *

from cloud.aws.utils.alarms import AWSAlarmReader, get_sns_topic_subscription_map

from cloud.aws.resource_classes.target_group import TargetGroupAWSResource
from cloud.aws.resource_classes.sqs_queue import SQSQueueAWSResourceGroup
from cloud.aws.resource_classes.load_balancer import LoadBalancerAWSResource
from cloud.aws.resource_classes.elasticache_redis import ElasticacheRedisAWSResource

resource_classes = [TargetGroupAWSResource, SQSQueueAWSResourceGroup, LoadBalancerAWSResource, ElasticacheRedisAWSResource]

def generate_pretty_table( resource_class, active_resources, region_unmonitored_resources_map,
                           regional_resource_type_alarm_action_map, business_team_map, sns_topic_subscription_map):
    
    '''
        This will create the table and write the header row in the format of  
        'Region', 'Resource Type' 'Business', 'Team', 'Service', 'SubService', 'Reason', 'Alarm'

    '''

    table = PrettyTable()

    # Adding Region And Resource type in header
    header_row = ['Region', resource_class.ACTIVE_RESOURCE_TYPE]

    # If SUPPRESS_ON_ANY_METRIC variale is set, then one more extra field is appended
    if not resource_class.SUPPRESS_ON_ANY_METRIC:
        header_row.append('Missing alarm metrics')

    # Adding other fields in the header
    header_row.extend([ 'Business', 'Team', 'Service', 'SubService', 'Reason', 'Alarm'])

    table.field_names = header_row

    for field in table.field_names:
        table.align[field] = 'l'

    # Creating more rows based on the details obtained from the map, like region name, resource_name etc.
    rows = get_rows_from_region_unmonitored_resources_map( region_unmonitored_resources_map, resource_class, business_team_map)

    rows.extend( get_rows_from_alarm_action_map( resource_class, active_resources, regional_resource_type_alarm_action_map,
                                                 region_unmonitored_resources_map, business_team_map, sns_topic_subscription_map, text_format=True))

    table.add_rows(rows)
    table.sort_by = "AZ"

    table_title = "Unmonitored {resource_verbose_name} metrics".format(
        resource_verbose_name=resource_class.VERBOSE_NAME)

    table_str = table.get_string(title=table_title)
    print(table_str)

    return len(rows)

def get_unmonitored_metric_for_resources( env, region, resource_class, alarm_reader, boto_client):

    '''
        This will find all those resources which  either dont contains the alarms, 
        or if contains the alarm so dont  have any SNS topic or endpoint to it.

    '''

    unmonitored_resource_metric_map = {}
    namespace = resource_class.NAMESPACE

    # Fetch all unmonitored resources 
    aws_resource = resource_class(env, region, boto_client)
    actice_resources = aws_resource.get_resources_to_monitor()

    # Fetch metric threshholds
    resource_class_metric_thresholds = alarm_reader.METRIC_THRESHOLDS.get( resource_class.ACTIVE_RESOURCE_TYPE, {})

    # Fetch metrics map for a namespace
    metrics_monitored_for_namespace = alarm_reader.MANDATORY_METRICS_MAP[namespace]
    for resource in actice_resources:
        readable_resource_name = (
            resource_class.get_readable_resource_name_from_arn( resource))

        metrics_with_threshold = resource_class_metric_thresholds.get(
            resource_class.get_resource_name_from_arn(resource), [])

        metrics_monitored_key = aws_resource.get_metrics_monitored_key(resource)
        metrics_monitored = metrics_monitored_for_namespace.get(
            metrics_monitored_key, set())

        if resource_class.SUPPRESS_ON_ANY_METRIC:
            if not metrics_monitored:
                unmonitored_resource_metric_map[readable_resource_name] = ''

        else:
            metrics_unmonitored = (
                set(MANDATORY_ALARM_METRICS[resource_class.ACTIVE_RESOURCE_TYPE]) - metrics_monitored)
            metrics_unmonitored = metrics_unmonitored - set(metrics_with_threshold)

            if metrics_unmonitored:
                unmonitored_resource_metric_map[readable_resource_name] = (
                    metrics_unmonitored)

    return aws_resource, actice_resources, unmonitored_resource_metric_map

def get_unmonitored_resources_for_region( env, region, resource_class, alarm_reader, boto_client):

    '''
       This will find all those resources for a specific region, which either dont contains the alarms, 
        or if contains the alarm so dont  have any SNS topic or endpoint to it. 
    '''

    aws_resource, active_resources, unmonitored_resources = get_unmonitored_metric_for_resources( env, region, resource_class, alarm_reader, boto_client)

    return region, active_resources, unmonitored_resources, aws_resource


def run_checker_for_resource(resource_class, env, regions, boto_clients, spreadsheet, business_team_map,
                             regional_alarm_readers, sns_topic_subscription_map):
    
    '''
        This will fetch all the unmonitored resources and alarm details for each region in a thread.
        Based on that, it will sent it to the spreadsheet.
    '''
    
    region_unmonitored_resources_map = {}
    regional_resource_type_alarm_action_map = {}

    region_pool = ThreadPoolExecutor(len(regions))
    region_futures = []
    
    
    for region in regions:

        '''
            Creates a regional_resource_type_alarm_action_map with reegion as key and  RESOURCE_TYPE_ALARM_ACTION_MAP as value
            ex.
            {
                "ap-south-1": {
                    "SQS_QUEUE" : ["queue_name", "alarm_name", "metric_name", "action_type", ["alarm_action1", "alarm_action1" ] ] 
                }
            }
        '''
        alarm_reader = regional_alarm_readers[region]
        regional_resource_type_alarm_action_map[region] = alarm_reader.RESOURCE_TYPE_ALARM_ACTION_MAP  # noqa: E501

        # Fetch all the resources per region which needs to be monitored.
        region_futures.append(region_pool.submit(
            get_unmonitored_resources_for_region, env, region, resource_class, alarm_reader, boto_clients[region]))

    for future in as_completed(region_futures):
        region, active_resources, unmonitored_resources, aws_resource = future.result()
        region_unmonitored_resources_map[region] = ( aws_resource, unmonitored_resources)

    # unique_resource_group = group_alarms_by_resource( regional_resource_type_alarm_action_map)

    generate_pretty_table(
        resource_class, active_resources, region_unmonitored_resources_map,
        regional_resource_type_alarm_action_map, business_team_map, sns_topic_subscription_map)

    n_rows = write_to_spreadsheet(
        spreadsheet, resource_class, active_resources,
        region_unmonitored_resources_map,
        regional_resource_type_alarm_action_map, business_team_map, sns_topic_subscription_map)

    return bool(n_rows)

def aws_alarm_checker(env, yaml_inputs, business_team_map, regions, spreadsheet_writer):

    # Getting the AWS access boto client and cloud watch boto client for different regions  
    resource_boto_clients = get_boto_clients(env, resource_classes, regions)
    cloudwatch_boto_clients = get_cloudwatch_boto_clients(env, regions)
    
    regional_alarm_readers = {}
    regional_sns_topic_subscription_map = {}

    # For different regions, information regarding all the alarms are fectched and store in different maps
    for region in regions:
        alarm_reader = AWSAlarmReader(cloudwatch_boto_clients[region])
        alarm_reader.read()

        regional_alarm_readers[region] = alarm_reader
        regional_sns_topic_subscription_map[region] = get_sns_topic_subscription_map(env, region)  # noqa: E501

    # As a part of this multiple threads will be created depending upon tthe number of resources to be examined.
    # All the unmonitored resources with their required details details are fetched and stores it in sheets
    resource_class_pool = ThreadPoolExecutor(len(resource_classes))
    resource_class_futures = []

    for resource_class in resource_classes:
        resource_class_futures.append(
            resource_class_pool.submit(
                run_checker_for_resource, resource_class, env, regions, resource_boto_clients[resource_class],
                spreadsheet_writer, business_team_map, regional_alarm_readers, regional_sns_topic_subscription_map))

    has_unmonitored_resources = False
    for future in as_completed(resource_class_futures):
        has_unmonitored_resources = future.result()
    
    return has_unmonitored_resources
