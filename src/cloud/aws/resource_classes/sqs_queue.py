import traceback
import botocore.exceptions

from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud.aws.utils.constants import ResourceType
from cloud.aws.resource_classes.base import BaseAWSResource


class SQSQueueAWSResourceGroup(BaseAWSResource):

    '''
        AWS SQS Resource Group Class
        
        This class determines all the queues present in specified region
        and stores ony thiose queues in map which dont contains INACTIVE tag.

        Also for all active queues the associated metric values are also find
        and only those queues are selected which have metric values > 0
    
    '''
    
    VERBOSE_NAME = 'SQS Queues'
    AWS_SERVICE_NAME = 'sqs'
    NAMESPACE = 'AWS/SQS'
    ACTIVE_METRIC_NAME = 'NumberOfMessagesSent'
    ACTIVE_STAT = 'Sum'
    ACTIVE_PERIOD = 7 * 24 * 60 * 60  # 7 days
    ACTIVE_RESOURCE_TYPE = ResourceType.SQS_QUEUE
    
    EXCLUDE_SUFFIX = 'celery-pidbox'
    # SUPPRESS_ON_ANY_METRIC = True

    def get_tag_for_queue(self, queue_url):

        '''

            This will return the queue Url and tag associated with the queue
        
        '''
        
        retry_count = 3
        retries = 0

        while retries < retry_count:
            try:
                # This will list all the tags present in a queue using queue url as a key to a boto3 function
                response = self.boto_client.list_queue_tags( QueueUrl=queue_url)
                break
            
            # If the client is overfilled then the ThrottLED error will be printed and retry will happen
            except botocore.exceptions.ClientError:
                print(queue_url, 'THROTTLED')
                retries += 1
                traceback.print_exc()
        
        # If all the retries are exhausted, then the particular queue will be ignored.
        if retries == retry_count:
            print(queue_url, 'FULL THROTTLED *****')

        return queue_url, response.get('Tags', {})

    def get_resource_tags_map(self, queue_urls):

        '''
        
            This will return the map containing queue name as key and tags as values
        
        '''
        pool = ThreadPoolExecutor(10)
        futures = []
        queue_url_tag_map = {}
        
        # Using threads , it will return the tag associated for each queue.
        for queue_url in queue_urls:

            futures.append(pool.submit(
                self.get_tag_for_queue, queue_url))

        for future in as_completed(futures):

            queue_url, tags = future.result()

            # This will extract out teh queue name from queue Url and 
            # then queue will be stored in map as key and its tag as value
            resource_name = self.get_readable_resource_name(queue_url)
            queue_url_tag_map[resource_name] = tags

        return queue_url_tag_map

    def get_resource_ids(self, resources):

        '''

            This function will return only those queues whose name dont ends 
            with EXCLUDE_SUFFIX i.e. 'celery_pid'
        
        '''
        
        return [
            queue_url for queue_url in resources
            if not queue_url.endswith(self.EXCLUDE_SUFFIX)
        ]

    def get_monitored_resources(self):

        '''

            This function will list out all the queues present in specific region of AWS account.
            After that, only those queues will be used which dont contain the INACTIVE tags.

        '''

        # List all the AWS SQS queues Urls present in the specific region
        all_resources = self.get_all_resources(
            paginator_name='list_queues',
            page_size=1000, resource_list_key='QueueUrls'
        )

        # List of all resources whcih dont contain the clery_pid in thier name
        filtered_resources = self.get_resource_ids(all_resources)

        # List of the resources not containing INACTIVE tag
        monitored_resources = self.filter_active_resources_by_monitor_tag(filtered_resources)

        return monitored_resources

    def get_resources_to_monitor(self):

        '''
            
            This is the first function which is being called whenever this class is used.
            It will find out all the active SQS resources for which alarms needs to be checked.
        
        '''
        
        # List all the queues which dont contains inactive tag and whose names dont ends with 'celery_pid'
        monitored_queues = self.get_monitored_resources()
        print('Number of sqs queues not having Inactive tag and celery_pid in name are: %s' % len(monitored_queues))

        # Creates resource names map with queue name as key and queue url as value.
        resource_names = {
            self.get_readable_resource_name(queue_url): queue_url
            for queue_url in monitored_queues
        }

        # This will list all those queues which contain the sum of metric values greater than 0.
        active_queues = self.get_active_resources(
            self.NAMESPACE, self.ACTIVE_METRIC_NAME, self.ACTIVE_STAT,
            self.ACTIVE_PERIOD, self.ACTIVE_RESOURCE_TYPE,
            resource_names.keys())

        print('No of sqs queues for which alarms needs to be checked are : %s' % len(active_queues))

        return active_queues

    @classmethod
    def get_readable_resource_name(cls, resource):

        return resource.split('/')[-1]

    @classmethod
    def get_readable_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split('/')[-1]

    @classmethod
    def get_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split('/')[-1]

    @classmethod
    def get_metrics_monitored_key(cls, resource_arn):
        
        return cls.get_readable_resource_name(resource_arn)