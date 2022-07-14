import json
import boto3
from collections import defaultdict

from cloud.aws.utils.secret import AWSSecretStoreSecret
from utils.utils import yaml_reader

def get_boto_clients(env, resource_classes, regions):

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
        for region in regions:

            boto_client = get_boto_client(env, resource_class.AWS_SERVICE_NAME, region)
            boto_clients[resource_class][region] = boto_client

    return boto_clients

def get_boto_client(env, service, region):

    '''
        Get boto client for accesing AWS for any env and region, from centralized secret store parameters.
    '''

    yaml_inputs = yaml_reader()
    inputs = yaml_inputs['awsAccessSecrets']
    
    if inputs['useAwsSecretManager'] == True:

        secret_name = inputs['secretName']
        secret_region = inputs['secretRegion']

        # Getting the secrets from store
        secret = json.loads(AWSSecretStoreSecret( secret_name, secret_region).get())

        ACCESS_KEY = secret['ACCESS_KEY']
        SECRET_KEY = secret['SECRET_KEY']

    else:

        ACCESS_KEY = inputs['aws_access_key']
        SECRET_KEY = inputs['aws_access_secret']

    # Returning the boto client 
    return boto3.client(
        service, region_name=region,
        aws_access_key_id=secret['ACCESS_KEY'],
        aws_secret_access_key=secret['SECRET_KEY'])


def get_cloudwatch_boto_clients(env, regions):

    ''' 
         Get cludwatch boto client for any env and region, from centralized secret store parameters.

    '''

    boto_clients = {}

    for region in regions:
        boto_clients[region] = get_boto_client( env, 'cloudwatch', region)

    return boto_clients