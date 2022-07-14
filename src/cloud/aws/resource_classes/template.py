# Template for adding any new resource in AWS Cloud for alarm checking
# For examples, refer any existing resource class

from concurrent.futures import ThreadPoolExecutor, as_completed

from cloud.aws.utils.constants import ResourceType
from utils.utils import get_chunked_list
from cloud.aws.resource_classes.base import BaseAWSResource

class <Resource_name>AWSResource(BaseAWSResource):

    '''
        Description for the class
    
    '''

    VERBOSE_NAME = '<Name of the resource to be checked>'
    AWS_SERVICE_NAME = '<Name of the service to be checked for a resource>'
    NAMESPACE = '<Namespace for a resource>'
    ACTIVE_METRIC_NAME = '<Metric Name to be taken in account>'
    ACTIVE_STAT = '<Name of Stat>'
    ACTIVE_PERIOD = <7 * 24 * 60 * 60  # 7 days>
    ACTIVE_RESOURCE_TYPE = ResourceType.<Resource name that will be added in ResourceType class in utilsconstants.py >

    def get_resource_tags_map_by_chunk(self, resource_arns):

        '''
            Returns Target Group's tag map from provided arns for a specific chunk of balancers

        '''

    def get_resource_tags_map(self, resource_arns):

        '''
            Returns map of resource name to their tags.
            This will be run in a thread, which in turn creating the map for a specific chunks 

        '''

    def get_resource_ids(self, resources):

        '''
            This will return the Target Group Arns from the provided full response 
        '''

    def get_monitored_resources(self):

        '''

            This function will list out all the Target Group present in specific region of AWS account.
            After that, only those TG will be used which dont contain the INACTIVE tags.

        '''

    def get_resources_to_monitor(self):

        '''     
            This is the first function which is being called whenever this class is used.
            It will find out all the active < Type of resource> resources for which alarms needs to be checked.

        '''

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