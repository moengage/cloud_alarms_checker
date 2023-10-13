import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from cloud.aws.utils.constants import MONITOR_TAG, MONITOR_TAG_INACTIVE_VALUE
from cloud.aws.utils.boto_client import get_boto_client
from utils.utils import get_chunked_list

class BaseAWSResource:

    '''

        This is the base class for aAWS Resources having common function required by all resources
    
    '''

    MANDATORY_ALARM_METRICS_WITH_THRESHOLD = []
    SUPPRESS_ON_ANY_METRIC = False

    def __init__(self, env,  dc, boto_client):

        self.env = env
        self.dc = dc
        self.boto_client = boto_client
        self.USED_RESOURCES = defaultdict(dict)
        self.ID_RESOURCE_MAP = {}
        self.RESOURCE_TAGS_MAP = {}

    def get_resources(self, page, resource_list_key):

        return page[resource_list_key]

    def get_resource_arns(self, resources):

        raise NotImplementedError

    def get_all_resources(self, paginator_name, page_size, resource_list_key):

        '''
        
            This function is called by its child resource classes i.e. SQS, TargetGroup etc.
            Returns the list of all the resources.
            Also creates the resource tag map.
        
        '''
        
        futures = []
        resources = []

        # This will list all resources in the form of pages 
        paginator = self.boto_client.get_paginator(paginator_name)
        response_iterator = paginator.paginate(
            PaginationConfig={
                'PageSize': page_size,
            }
        )

        pool = ThreadPoolExecutor(20)
        
        # This will stores all the resources obtained in multiple pages into a resources list using threads
        for page in response_iterator:

            futures.append(pool.submit(
                self.get_resources, page, resource_list_key))

        for future in as_completed(futures):

            resources.extend(future.result())

        self.RESOURCE_TAGS_MAP = self.get_resource_tags_map(
            self.get_resource_ids(resources))

        return resources

    def get_resource_tags_map(self, resources):

        raise NotImplementedError

    
    def filter_active_resources_by_monitor_tag(self, resources):
        
        active_resouces = []
        
        # This will find out all the resource names from the resource arns
        for resource_arn in resources:
            resource_name = self.get_readable_resource_name(resource_arn)

            # This will find out the tag value from the map
            monitor_tag_value = self.RESOURCE_TAGS_MAP[
                resource_name].get(MONITOR_TAG)
            
            # In this the tag value is checked against INACTIVE tag value
            # If the tag is not inactive , then the resources are appended active resources list.
            if monitor_tag_value != MONITOR_TAG_INACTIVE_VALUE:
                active_resouces.append(resource_arn)

        return active_resouces
    

    def get_cloudwatch_active_metric_query( self, namespace, metric_name, resource_type, resource_name, period, stat):

        '''

            This will create the metric query for the specified resource

        '''
         
         # Metric query Id in the form of Metric_Name.ResourceName i.e. 'NumberOfMessagesSent.AwsSQSQueueName'
        _id = '{metric_name}.{resource_name}'.format(metric_name=metric_name, resource_name=resource_name)

        _id = _id.replace('-', '_')
        _id = _id.replace('.', '_')
        _id = _id.replace('/', '_')
        _id = _id.lower()

        # Map containing id as key and resource_name and metric_name as values
        self.ID_RESOURCE_MAP[_id] = (resource_name, metric_name)

        # Returns the query in the form of 
        '''
        {
            'Id': 'string',  
            'MetricStat': {
                'Metric': {
                    'Namespace': 'string',
                    'MetricName': 'string',
                    'Dimensions': [
                        {
                            'Name': 'string',
                            'Value': 'string'
                        },
                    ]
                },
                'Period': 123,
                'Stat': 'string',
             },
        }
        '''

        return {
            'Id': _id,
            'MetricStat': {
                'Metric': {
                    'Namespace': namespace,
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': resource_type,
                            'Value': resource_name
                        },
                    ]
                },
                'Period': period,
                'Stat': stat,
            },
            'ReturnData': True,
        }

    def get_metric_queries_for_resources(self, namespace, metric_name, stat, period, resource_type, resource_names):

        '''

            This will return the list of metric queries for a resource

        '''

        metric_queries = []

        for resource_name in resource_names:
            metric_queries.append(self.get_cloudwatch_active_metric_query(
                namespace, metric_name, resource_type, resource_name, period, stat
            ))

        return metric_queries

    def get_active_resources(self, namespace, metric_name, stat, period, resource_type, resource_names):
        
        '''
        
            This will return the list of all those resources whose sum of metric values is greater than 0

        '''

        # This will store all metric querries obtained for the resources into the list
        metric_queries = self.get_metric_queries_for_resources(
            namespace, metric_name, stat, period, resource_type, resource_names)

        # This will get the metric data based on the metric queries obtained above
        # Also as part of this a map of resource_name, metric_name as keys and sum(metric_values) as value is obtained
        self.set_metric_data(metric_queries)

        # This will store only those resources in active_resources list
        # whose sum(metric_values) are greter than 0
        active_resource_names = []
        for resource_name, metrics in self.USED_RESOURCES.items():

            if sum(metrics.values()) > 0:
                active_resource_names.append(resource_name)

        return active_resource_names

    def set_metric_data(self, metric_queries):
        '''

            This will get the metric data based on meyric queries
            To get the metric data for a resource, boto3 get_metric_data functio  is used
        
        '''

        now = datetime.datetime.now()
        start_timestamp = now - datetime.timedelta(days=7)
        end_timestamp = now

        # This will create an iterator for  metric data for a particular region in cloudwatch 
        boto_client = get_boto_client(self.env, 'cloudwatch', '', self.dc)
        paginator = boto_client.get_paginator('get_metric_data')

        # This will create the list of list containing each list having chunks with 500 metric queries
        # Ex [ [ 500 metric queries ], .....]
        metric_query_chunks = get_chunked_list(metric_queries, chunk_size=500)

        threads = len(metric_query_chunks)
        if threads > 10:
            threads = 10

        chunk_count = 0
        pool = ThreadPoolExecutor(threads)
        futures = []
        
        # For each list of chunk it will get the metric data 
        for metric_query_chunk in metric_query_chunks:
            chunk_count += 1
            futures.append(pool.submit(
                self.set_metric_data_for_chunk, paginator, metric_query_chunk,
                start_timestamp, end_timestamp, chunk_count,
                total_chunks=len(metric_query_chunks)
            ))

        for future in as_completed(futures):
            future.result()


    def set_metric_data_for_chunk(self, paginator, metric_queries, start_timestamp, end_timestamp, chunk_count, total_chunks):
        '''

            This will get the metric data for a provided chunk of metric queries for specific resources in specific region
            Once the metric data is obtained, a map is created as follows
            map = {
                "resource_name" = {
                    "metric_name" = {
                        sum(metric_values)
                    }
                }
            }
        
        '''

        metric_ids = []
        filtered_metric_queries = []

        # This will filter out the unique metric queries into a new list
        # By filtering it means that, if the metric query Id is not present in metric_ids list, then it is stored in both metric_ids and filtered_metric_queries
        # Otherwise the metric query will be ignored
        for metric_query in metric_queries:
            if not metric_query['Id'] in metric_ids:
                filtered_metric_queries.append(metric_query)

            metric_ids.append(metric_query['Id'])

        # This will get the metric data for all the required filtered metric queries
        response_iterator = paginator.paginate(
            MetricDataQueries=filtered_metric_queries,
            StartTime=start_timestamp,
            EndTime=end_timestamp,
            ScanBy='TimestampAscending',
            LabelOptions={
                'Timezone': '+0530'
            },
            PaginationConfig={
                'PageSize': 100800,
            }
        )

        # Example output of Get_metric_data
        '''
        {
            'MetricDataResults': [
                {
                    'Id': 'string',
                    'Label': 'string',
                    'Timestamps': [
                        datetime(2015, 1, 1),
                    ],
                    'Values': [
                        123.0,
                    ],
                    'StatusCode': 'Complete'|'InternalError'|'PartialData',
                    'Messages': [
                        {
                            'Code': 'string',
                            'Value': 'string'
                        },
                    ]
                },
            ],
            'NextToken': 'string',
            'Messages': [
                {
                    'Code': 'string',
                    'Value': 'string'
                },
            ]
        }
        '''

        page_count = 0
        for page in response_iterator:
            
            page_count += 1
            print('Processing page %s for chunk %s/%s' % (page_count, chunk_count, total_chunks))

            # creating resource_name, metric_name and sum(metric_value) map for later use
            for metric_data in page['MetricDataResults']:

                metric_value = sum(metric_data['Values'])
                resource_name, metric_name = self.ID_RESOURCE_MAP[
                    metric_data['Id']]
                self.USED_RESOURCES[resource_name][metric_name] = metric_value

    @classmethod
    def get_readable_resource_name(cls, resource):
        return resource