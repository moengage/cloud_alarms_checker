import json
import boto3
from collections import defaultdict

from cloud.aws.utils.secret import AWSSecretStoreSecret
from utils.utils import yaml_reader
from botocore.config import Config

def get_boto_clients(env, resource_classes, dcs, yaml_inputs):

    '''
        This will create a map of boto clients for each region.
        ex.
        {
            "SQS_QUEUE": {
                "ap-south-1" : "boto_client_details"
            }
        }

    '''

    boto_clients = defaultdict(dict)

    for resource_class in resource_classes:
        for dc in dcs:
            region = yaml_inputs['env_region_map'][dc]['region']
            boto_client = get_boto_client(env, resource_class.AWS_SERVICE_NAME, region, dc)
            boto_clients[resource_class][dc] = boto_client

    return boto_clients

def get_boto_client(env, service, region, dc):

    '''
        Get boto client for accesing AWS for any env and region, from centralized secret store parameters.
    '''

    yaml_inputs = yaml_reader()
    
    if region == '':
        region = yaml_inputs['env_region_map'][dc]['region']
        
    inputs = yaml_inputs['awsAccessSecrets']
    
    env_region_map = yaml_inputs['env_region_map']
    
    if inputs['useAwsSecretManager'] == True:

        secret_name = env_region_map[dc]['secret_name']
        secret_region = env_region_map[dc]['secretRegion']

        # Getting the secrets from store
        secret = json.loads(AWSSecretStoreSecret( secret_name, secret_region).get())

        ACCESS_KEY = secret['ACCESS_KEY']
        SECRET_KEY = secret['SECRET_KEY']

    else:

        ACCESS_KEY = env_region_map[dc]['aws_access_key']
        SECRET_KEY = env_region_map[dc]['aws_access_secret']

    # Returning the boto client 
    config = Config(retries=dict(max_attempts=10))
    return boto3.client(
        service, region_name=region,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config = config)


def get_cloudwatch_boto_clients(env, regions, yaml_inputs):

    ''' 
         Get cludwatch boto client for any env and region, from centralized secret store parameters.

    '''

    boto_clients = {}

    for dc in regions:
        region = yaml_inputs['env_region_map'][dc]['region']
        boto_clients[dc] = get_boto_client( env, 'cloudwatch', region, dc)

    return boto_clients

def get_sns_boto_clients(env, regions, yaml_inputs):

    ''' 
         Get sns boto client for any env and region, from centralized secret store parameters.

    '''

    boto_clients = {}

    for dc in regions:
        region = yaml_inputs['env_region_map'][dc]['region']
        boto_clients[dc] = get_boto_client( env, 'sns', region, dc)

    return boto_clients