from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud.aws.utils.constants import ResourceType
from utils.utils import get_chunked_list
from cloud.aws.resource_classes.base import BaseAWSResource

class LoadBalancerAWSResource(BaseAWSResource):

    '''
        AWS Load Balancer Resource Group Class
        
        This class determines all the LB present in specified region
        and stores ony those LB in map which dont contains INACTIVE tag.

        Also for all active LB the associated metric values are also find
        and only those LB are selected which have metric values > 0
    
    '''

    VERBOSE_NAME = 'EC2 App Load Balancer'
    AWS_SERVICE_NAME = 'elbv2'
    NAMESPACE = 'AWS/ApplicationELB'
    ACTIVE_METRIC_NAME = 'RequestCount'
    ACTIVE_STAT = 'Sum'
    ACTIVE_PERIOD = 7 * 24 * 60 * 60  # 7 days
    ACTIVE_RESOURCE_TYPE = ResourceType.LOAD_BALANCER

    def get_resource_tags_map_by_chunk(self, resource_arns):

        '''
            Returns Load Balancer's tag map from provided arns for a specific chunk of balancers

        '''

        resource_arn_tags_map = {}

        response = self.boto_client.describe_tags( ResourceArns=resource_arns)

        for item in response['TagDescriptions']:

            # Creating the map of tags for a specific resource
            tags = {tag['Key']: tag['Value'] for tag in item['Tags']}
            
            # Fetching the resource name from the arn
            resource_name = self.get_readable_resource_name_from_arn( item['ResourceArn'])
            
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

            futures.append(pool.submit(
                self.get_resource_tags_map_by_chunk, chunk))

        # Combining all chunks output into one map
        for future in as_completed(futures):

            resource_name_tags_map.update(future.result())

        return resource_name_tags_map

    def get_resource_ids(self, resources):

        '''
            This will return the load balancer ids from the provided full response 
        '''

        return [
            resource['LoadBalancerArn'] for resource in resources]

    def get_monitored_resources(self):

        '''

            This function will list out all the load balancers present in specific region of AWS account.
            After that, only those balancers will be used which dont contain the INACTIVE tags.

        '''

        # List all the AWS LB present in the specific region
        all_resources = self.get_all_resources(
            paginator_name='describe_load_balancers',
            page_size=400, resource_list_key='LoadBalancers'
        )

        # Finds the LB arn/url from the output of above step
        all_resource_arns = self.get_resource_ids(all_resources)
        print('ALL RESOURCES COUNT: %s' % len(all_resources))
        
        monitored_resources = self.filter_active_resources_by_monitor_tag(all_resource_arns)

        return monitored_resources
        #return all_resource_arns

    def get_resources_to_monitor(self):

        '''     
            This is the first function which is being called whenever this class is used.
            It will find out all the active Load Balancer resources for which alarms needs to be checked.
        
        '''

        # List all the LB which dont contains inactive tag.
        monitored_resource_arns = self.get_monitored_resources()
        print('Number of Load Balancers not having Inactive tag: %s' % len(monitored_resource_arns))

        # Creates resource names map with LB name as key and LB arn as value.
        resource_name_arn_map = {
            '/'.join(resource_arn.split(":")[-1].split("/")[1:]): resource_arn
            for resource_arn in monitored_resource_arns
        }

        # This will list all those LB which contain the sum of metric values greater than 0.
        active_resource_names = self.get_active_resources(
            self.NAMESPACE, self.ACTIVE_METRIC_NAME, self.ACTIVE_STAT,
            self.ACTIVE_PERIOD, self.ACTIVE_RESOURCE_TYPE,
            resource_name_arn_map.keys())

        print('No of Load Balancers for which alarms needs to be checked are : %s' % len(active_resource_names))

        return [
            resource_name_arn_map[resource_name]
            for resource_name in active_resource_names
        ]

    @classmethod
    def get_readable_resource_name(cls, resource):

        return resource.split('/')[2]

    @classmethod
    def get_readable_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split(':')[-1].split("/")[2]

    @classmethod
    def get_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split(':')[-1]

    @classmethod
    def get_metrics_monitored_key(cls, resource_arn):
        
        resource_identifier = cls.get_resource_name_from_arn(resource_arn)
        return "/".join(resource_identifier.split("/")[1:])