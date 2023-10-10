import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud.aws.utils.constants import ResourceType
from utils.utils import get_chunked_list
from cloud.aws.resource_classes.base import BaseAWSResource

class ElasticacheRedisAWSResource(BaseAWSResource):

    '''
        AWS Elasticcache Redis Resource Group Class
        
        This class determines all the Elasticache Redis present in specified region
        and stores ony those Elasticache Redis in map which dont contains INACTIVE tag.

        Also for all active Elasticache Redis the associated metric values are also find
        and only those Elasticache Redis are selected which have metric values > 0
    
    '''

    VERBOSE_NAME = 'Elasticache Redis'
    AWS_SERVICE_NAME = 'elasticache'
    NAMESPACE = 'AWS/ElastiCache'
    ACTIVE_METRIC_NAME = 'GetTypeCmds'
    ACTIVE_STAT = 'Sum'
    ACTIVE_PERIOD = 7 * 24 * 60 * 60  # 7 days
    ACTIVE_RESOURCE_TYPE = ResourceType.REDIS_CACHE_CLUSTER

    def get_resource_tags_map_by_chunk(self, resource_arn):

        '''
            Returns Elasticache Redis tag map from provided arns for a specific chunk of resources

        '''

        resource_arn_tags_map = {}
        retries = 3
        retry_count = 0
        
        # Retrying to fetch the tag for a resource with count of 3
        while retry_count < retries:

            try:
                retry_count += 1

                # Finding the resource name  from resource arn
                resource_name = self.get_readable_resource_name_from_arn(
                    resource_arn)
                
                resource_arn_tags_map[resource_name] = {}

                # Listing the tags for a particular resource
                response = self.boto_client.list_tags_for_resource(
                    ResourceName=resource_arn)

                tags = {
                    tag['Key']: tag['Value'] for tag in response['TagList']}

                resource_arn_tags_map[resource_name] = tags

            except self.boto_client.exceptions.CacheClusterNotFoundFault:
                retry_count += 1
                traceback.print_exc()
                time.sleep(30)
                
                
            except Exception:
                pass
        # print("Elasticache Tags for all the cluster arn")
        # print(resource_arn_tags_map)
        return resource_arn_tags_map

    def get_resource_tags_map(self, resource_arns):

        '''
            Returns map of resource name to their tags.
            This will be run in a thread, which in turn creating the map for a specific chunks 

        '''

        MAX_ITEMS_PER_CALL = 1
        resource_name_tags_map = {}

        # Creating a chunk of 20 resources from the list of all resources
        chunked_resource_arns = get_chunked_list(   resource_arns, MAX_ITEMS_PER_CALL)

        pool = ThreadPoolExecutor(MAX_ITEMS_PER_CALL)
        futures = []

        # Creating a map of resource names to their tags for a specified chunks
        for chunk in chunked_resource_arns:

            futures.append(pool.submit( self.get_resource_tags_map_by_chunk, chunk[0]))

        # Combining all chunks output into one map
        for future in as_completed(futures):

            resource_name_tags_map.update(future.result())

        # print("Elasticache Tags map with the cache name for all the cluster id")
        # print(resource_name_tags_map)
        return resource_name_tags_map

    def get_resource_ids(self, resources):

        '''
            This will return the Elasticcache Redis ids from the provided full response 
        '''

        return [
            resource['ARN'] for resource in resources]

    def get_monitored_resources(self):

        '''

            This function will list out all the Elasticcache Redis present in specific region of AWS account.
            After that, only those Elasticcache Redis will be used which dont contain the INACTIVE tags.

        '''
        
        # List all the AWS Elasticcache Redis present in the specific region
        all_resources = self.get_all_resources(
            paginator_name='describe_cache_clusters',
            page_size=100, resource_list_key='CacheClusters'
        )

        print('ALL RESOURCES COUNT: %s' % len(all_resources))
        all_resource_arns = self.get_resource_ids(all_resources)

        # monitored_resources = self.filter_active_resources_by_monitor_tag(all_resource_arns)
        monitored_resources = all_resource_arns

        return monitored_resources
        #return all_resource_arns

    def get_resources_to_monitor(self):

        '''     
            This is the first function which is being called whenever this class is used.
            It will find out all the active Elasticcache Redis resources for which alarms needs to be checked.
        
        '''

        # List all the Elasticcache Redis which dont contains inactive tag.
        monitored_resource_arns = self.get_monitored_resources()
        # print('Number of Elasticcache Redis not having Inactive tag: %s' % len(monitored_resource_arns))

        # Creates resource names map with Elasticcache Redis name as key and Elasticcache Redis arn as value.
        resource_name_arn_map = {
            resource_arn.split(":")[-1]: resource_arn
            for resource_arn in monitored_resource_arns
        }

        # This will list all those Elasticcache Redis which contain the sum of metric values greater than 0.
        # active_resource_names = self.get_active_resources(
        #     self.NAMESPACE, self.ACTIVE_METRIC_NAME, self.ACTIVE_STAT,
        #     self.ACTIVE_PERIOD, self.ACTIVE_RESOURCE_TYPE,
        #     resource_name_arn_map.keys())
        active_resource_names = resource_name_arn_map.keys()
        print("Active Resource Name")
        print(active_resource_names)

        print('No of Elasticcache Redis for which alarms needs to be checked are : %s' % len(active_resource_names))

        return [
            resource_name_arn_map[resource_name]
            for resource_name in active_resource_names
        ]

    @classmethod
    def get_readable_resource_name(cls, resource_arn):

        return resource_arn.split(':')[-1]

    @classmethod
    def get_readable_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split(':')[-1]

    @classmethod
    def get_resource_name_from_arn(cls, resource_arn):

        return resource_arn.split(':')[-1]

    @classmethod
    def get_metrics_monitored_key(cls, resource_arn):
        
        return cls.get_readable_resource_name(resource_arn)