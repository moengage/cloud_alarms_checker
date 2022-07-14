from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud.aws.utils.constants import ResourceType
from utils.utils import get_chunked_list
from cloud.aws.resource_classes.base import BaseAWSResource


class TargetGroupAWSResource(BaseAWSResource):

    '''
        AWS Target Group Resource Group Class
        
        This class determines all the Target Group present in specified region
        and stores ony those Target Group in map which dont contains INACTIVE tag.

        Also for all active Target Group the associated metric values are also find
        and only those Target Group are selected which have metric values > 0
    
    '''

    VERBOSE_NAME = 'EC2 Target Group'
    AWS_SERVICE_NAME = 'elbv2'
    NAMESPACE = 'AWS/ApplicationELB'
    ACTIVE_METRIC_NAME = 'RequestCountPerTarget'
    ACTIVE_STAT = 'Sum'
    ACTIVE_PERIOD = 7 * 24 * 60 * 60  # 7 days
    ACTIVE_RESOURCE_TYPE = ResourceType.TARGET_GROUP

    def get_resource_tags_map_by_chunk(self, resource_arns):

        '''
            Returns Target Group's tag map from provided arns for a specific chunk of balancers

        '''

        resource_arn_tags_map = {}

        response = self.boto_client.describe_tags( ResourceArns=resource_arns)

        # Creating the map of tags for a specific resource
        for item in response['TagDescriptions']:

            tags = {tag['Key']: tag['Value'] for tag in item['Tags']}
            
            # Fetching the resource name from the arn
            resource_name = self.get_readable_resource_name_from_arn(
                item['ResourceArn'])

            # Storing the tags in the map where resource_name is the key and map of tags is the value
            resource_arn_tags_map[resource_name] = tags

        return resource_arn_tags_map

    def get_resource_tags_map(self, resource_arns):

        '''
            Returns map of resource name to their tags.
            This will be run in a thread, which in turn creating the map for a specific chunks 

        '''
        
        MAX_ITEMS_PER_CALL = 20
        resource_name_tags_map = {}

        # Creating a chunk of 20 resources from the list of all resources
        chunked_resource_arns = get_chunked_list( resource_arns, MAX_ITEMS_PER_CALL)

        pool = ThreadPoolExecutor(MAX_ITEMS_PER_CALL)
        futures = []

        # Creating a map of resource names to their tags for a specified chunks
        for chunk in chunked_resource_arns:

            futures.append(pool.submit( self.get_resource_tags_map_by_chunk, chunk))

        # Combining all chunks output into one map
        for future in as_completed(futures):

            resource_name_tags_map.update(future.result())

        return resource_name_tags_map

    def get_resource_ids(self, resources):

        '''
            This will return the Target Group Arns from the provided full response 
        '''

        return [resource['TargetGroupArn'] for resource in resources]

    def get_monitored_resources(self):

        '''

            This function will list out all the Target Group present in specific region of AWS account.
            After that, only those TG will be used which dont contain the INACTIVE tags.

        '''

        # List all the AWS TG present in the specific region
        all_resources = self.get_all_resources(
            paginator_name='describe_target_groups',
            page_size=400, resource_list_key='TargetGroups'
        )
        
        # Finds the TG arn/url from the output of above step
        filtered_resources = self.get_resource_ids(all_resources)      
        print('ALL RESOURCES COUNT: %s' % len(all_resources))
        
        #monitored_resources = self.filter_active_resources_by_monitor_tag(filtered_resources)

        #return monitored_resources
        return filtered_resources

    def get_resources_to_monitor(self):

        '''     
            This is the first function which is being called whenever this class is used.
            It will find out all the active Target Group resources for which alarms needs to be checked.
        
        '''

        # List all the TG which dont contains inactive tag.
        monitored_resource_arns = self.get_monitored_resources()
        print('Number of Target Groups not having Inactive tag: %s' % len(monitored_resource_arns))

        # Creates resource names map with TG name as key and TG arn as value.
        resource_name_arn_map = {
            resource_arn.split(":")[-1]: resource_arn
            for resource_arn in monitored_resource_arns
        }

         # This will list all those TG which contain the sum of metric values greater than 0.
        active_resource_names = self.get_active_resources(
            self.NAMESPACE, self.ACTIVE_METRIC_NAME, self.ACTIVE_STAT,
            self.ACTIVE_PERIOD, self.ACTIVE_RESOURCE_TYPE,
            resource_name_arn_map.keys())

        print('No of Target Groups for which alarms needs to be checked are : %s' % len(active_resource_names))

        return [
            resource_name_arn_map[resource_name]
            for resource_name in active_resource_names
        ]

    @classmethod
    def get_readable_resource_name(cls, resource):

        return resource.split('/')[1]

    @classmethod
    def get_readable_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split(':')[-1].split("/")[1]

    @classmethod
    def get_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split(':')[-1]

    @classmethod
    def get_metrics_monitored_key(cls, resource_arn):
        
        return cls.get_resource_name_from_arn(resource_arn)