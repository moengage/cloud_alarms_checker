from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud.aws.utils.constants import METRIC_RESOURCE_TYPE_MAP
from cloud.aws.utils.utils import get_resource_name_from_dimensions
from cloud.aws.utils.boto_client import get_boto_client


class AWSAlarmReader():

    ALARM_METRICS_WITH_THRESHOLD = {
        'HealthyHostCount': [
            {
                'Threshold': 0,
                'ComparisonOperator': 'LessThanOrEqualToThreshold'
            },
            {
                'Threshold': 1,
                'ComparisonOperator': 'LessThanThreshold'
            },
        ]
    }

    def __init__(self, boto_client):
        self.boto_client = boto_client
        self.MANDATORY_METRICS_MAP = defaultdict(dict)
        self.METRIC_THRESHOLDS = defaultdict(dict)
        self.RESOURCE_TYPE_ALARM_ACTION_MAP = defaultdict(list)

    def set_mandatory_metric_with_threshold(self, metric):

        '''
            This is used to create METRIC_THRESHOLDS map of all those alarms which contains the required thresholds.

        '''

        for metric_group, metric_group_values in self.ALARM_METRICS_WITH_THRESHOLD.items():
            thresholds_match = False
            for threshold in metric_group_values:
                if metric['MetricName'] != metric_group:
                    continue
                if (threshold['Threshold'] == metric.get('Threshold') and
                        threshold['ComparisonOperator'] ==
                        metric.get('ComparisonOperator')):
                    thresholds_match = True
                    break

            if not thresholds_match:
                return

            resource_name = ''
            dimension_name = METRIC_RESOURCE_TYPE_MAP[metric_group]
            for dimension in metric['Dimensions']:
                if dimension['Name'] == dimension_name:
                    resource_name = dimension['Value']
                    break

            if resource_name not in self.METRIC_THRESHOLDS[dimension_name]:
                self.METRIC_THRESHOLDS[dimension_name][resource_name] = []

            self.METRIC_THRESHOLDS[dimension_name][resource_name].append(
                metric_group)

    def set_data_in_mandatory_metrics_map(self, metric):
        
        '''
            This will create a MANDATORY_METRICS_MAP which contains namespace as the key and the value as another map
            whose key is dimension_value and value as metric_name

            ex {
                "AWS/EC2" : {
                    "i-0c986c72" : "CPUUtilization"
                }
            }

        '''
        
        namespace = metric['Namespace']
        metric_name = metric['MetricName']

        for dimension in metric['Dimensions']:
            dimension_value = dimension['Value']

            # If dimesion value is not present, then internal map will be set and added to it, otherwise will  be ignored
            if dimension_value not in self.MANDATORY_METRICS_MAP[namespace]:
                self.MANDATORY_METRICS_MAP[namespace][dimension_value] = set()

            self.MANDATORY_METRICS_MAP[namespace][dimension_value].add(
                metric_name)

    def capture_alarm_action(self, alarm_arn, alarm_name, alarm_actions, metric_name, dimensions): 

        '''
            This will capture whether the alarm has any action( ex. SNS topic) associated to it or not
            Also if the action is not present, then it is checked whether it is a child of some other alarm
            and then its parent action is checked.

            As a result of it RESOURCE_TYPE_ALARM_ACTION_MAP is created.
            ex
            {
                "SQS_QUEUE" : ["queue_name", "alarm_name", "metric_name", "action_type", ["alarm_action1", "alarm_action1" ] ] 
            }
        '''

        # Finding the type of resource( ex. SQS_QUEUE ) from the metric_name-resource_type map
        resource_type = METRIC_RESOURCE_TYPE_MAP.get(metric_name)
        if not resource_type:
            return

        # Finding the resource name from the dimensions list
        resource_name = get_resource_name_from_dimensions( resource_type, dimensions)

        action_types = []

        # If the current alarm doesnt contain any action, then checking for its parent alarm, if exits
        if len(alarm_actions) == 0 :

            # This will return the parent alarm names in list format.
            parent_alarm_response = self.boto_client.describe_alarms(
                ParentsOfAlarmName = alarm_name
            )

            # if parent alarm exist, then describing it to get the associated alarm action.
            if len(parent_alarm_response['CompositeAlarms']) != 0 :

                parent_alarm_details_response = self.boto_client.describe_alarms(
                    AlarmNames = [ alarm['AlarmName'] for alarm in parent_alarm_response['CompositeAlarms'] ],
                    AlarmTypes=[
                        'CompositeAlarm'
                    ],
                )

                alarm_actions = []
                for alarm in parent_alarm_details_response['CompositeAlarms']:
                    for action in alarm['AlarmActions']:
                          alarm_actions.append(action)
        
        # Creating the resource and alarm action map for future use.
        for action in alarm_actions:
            action_types.append(action.split(':')[2])

        action_types = list(set(action_types))

        self.RESOURCE_TYPE_ALARM_ACTION_MAP[resource_type].append([
                resource_name, alarm_name, metric_name, action_types,
                alarm_actions])

    def set_mandatory_metrics_map_for_page(self, page):

        '''
            For a particular page obtained from describing the alarms, different kinds of maps are created
            which will be used in future

        '''

        metric_alarms = page['MetricAlarms']

        for alarm in metric_alarms:

            # If NameSpace is present in alarms, then directly different details will be captured.
            if 'Namespace' in alarm:
                self.set_data_in_mandatory_metrics_map(alarm)
                self.set_mandatory_metric_with_threshold(alarm)
                self.capture_alarm_action( alarm['AlarmArn'], alarm['AlarmName'], alarm['AlarmActions'],
                                           alarm['MetricName'], alarm['Dimensions'])

            # Metric Stat is present in alarms, then the required details details will be fetched from these as well
            # this is useful in the case of compoite alarms
            # Commented the below block to fix the issue which is occuring if the resource ( Ex. SQS ) is a part of multimetric alarm.
            # Than the value (Resource Name - queue_name) is not showing up in the final spreadsheet result, as ideally it should come.
#             for metric in alarm.get('Metrics', []):
#                 if 'MetricStat' not in metric:
#                     continue

#                 _metric = metric['MetricStat']['Metric']
#                 self.set_data_in_mandatory_metrics_map(_metric)
#                 self.set_mandatory_metric_with_threshold(_metric)
#                 self.capture_alarm_action( alarm['AlarmArn'], alarm['AlarmName'], alarm['AlarmActions'],
#                                            _metric['MetricName'], _metric['Dimensions'])

    def read(self):

        '''
            This is the function which is first invoked in this class
            This will fetch all alarms along with thier details present in a specific region 

        '''
        
        # This will print all the alarms present in a region along with thier full information
        # Ex
        '''
            {
                "MetricAlarms": [
                {
                    "EvaluationPeriods": 2,
                    "AlarmArn": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:myalarm",
                    "StateUpdatedTimestamp": "2014-04-09T18:59:06.442Z",
                    "AlarmConfigurationUpdatedTimestamp": "2012-12-27T00:49:54.032Z",
                    "ComparisonOperator": "GreaterThanThreshold",
                    "AlarmActions": [
                        "arn:aws:sns:us-east-1:123456789012:myHighCpuAlarm"
                    ],
                    "Namespace": "AWS/EC2",
                    "AlarmDescription": "CPU usage exceeds 70 percent",
                    "StateReasonData": "{\"version\":\"1.0\",\"queryDate\":\"2014-04-09T18:59:06.419+0000\",\"startDate\":\"2014-04-09T18:44:00.000+0000\",\"statistic\":\"Average\",\"period\":300,\"recentDatapoints\":[38.958,40.292],\"threshold\":70.0}",
                    "Period": 300,
                    "StateValue": "OK",
                    "Threshold": 70.0,
                    "AlarmName": "myalarm",
                    "Dimensions": [
                    {
                        "Name": "InstanceId",
                        "Value": "i-0c986c72"
                    }],
                    "Statistic": "Average",
                    "StateReason": "Threshold Crossed: 2 datapoints were not greater than the threshold (70.0). The most recent datapoints: [38.958, 40.292].",
                    "InsufficientDataActions": [],
                    "OKActions": [],
                    "ActionsEnabled": true,
                    "MetricName": "CPUUtilization"
                }]
            }     
        '''

        paginator = self.boto_client.get_paginator('describe_alarms')
        response_iterator = paginator.paginate(
            PaginationConfig={
                'PageSize': 100,
            }
        )

        pool = ThreadPoolExecutor(20)
        futures = []

        # Creating different required maps per page
        for page in response_iterator:
            futures.append(pool.submit(
                self.set_mandatory_metrics_map_for_page, page))

        for future in as_completed(futures):
            future.result()


def get_sns_topic_subscription_map(env, region):
    '''
        This will fetch the SNS topic details and stores it in topic_subscription_map map

    '''

    topic_subscription_map = defaultdict(list)

    # Creating a boto client for sns topic
    boto_client = get_boto_client(env, 'sns', region)
    
    # Ths will list out all sns subscriptions in the form of pages
    paginator = boto_client.get_paginator('list_subscriptions')
    response_iterator = paginator.paginate()

    for page in response_iterator:
        for subscription in page['Subscriptions']:

            topic_arn = subscription['TopicArn']
            subscription_arn = subscription['SubscriptionArn']

            # AMp is created in which topic_arn will be the key and subscription_arn will be the value
            topic_subscription_map[topic_arn].append(subscription_arn)

    return topic_subscription_map
