import boto3
import base64
from botocore.exceptions import ClientError

class AWSSecretStoreSecret:

    '''
    This will fetch secrets from the AWS Secret Store by providing the secret name and the region in which it is present

    '''

    def __init__(self, secret_name, region_name):

        # Name of the secret and the region in which it is present
        self.secret_name = secret_name
        self.region_name = region_name

    def get(self):

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )

        try:

            # Fetching all secrets store in a specified secret name
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name)
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text
                # using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your
                # discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':  # noqa: E501
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your
                # discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your
                # discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the
                # current state of the resource.
                # Deal with the exception here, and/or rethrow at your
                # discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your
                # discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of
            # these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(
                    get_secret_value_response['SecretBinary'])
                return decoded_binary_secret