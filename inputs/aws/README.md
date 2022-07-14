# Input Yaml Format

To make the project more generic, yaml based inputs are added to the project.

For example in case of AWS, following are description of fields:

1. Create a example Input file for aws that is added or being in use.

2. In the specification, mention which `cloud:aws` to tell this is for `aws` to be used.

3. In `exclude_resources_on_tags`, add the tags, by which the script will understand the resources that contain these tags are exempted to check for alarms.  
    **NOTE**- Only single tag is allowed in this case. For using more than one tags, then code chnages are required in resource_classes

4. In `resources_to_ckeck`, add the names of resource class to be checked for alarms.  
    **NOTE**- To add any new resource, follow the [README.md](../src/cloud/aws/resource_classes/README.md)

5. In `awsAccessSecrets`, provide the ways of accessing the AWS     
    - You can store the secrets in AWS Secret Manager  
    - You can directly provide the secrets in the inputs file.  

    **NOTE**- New ways of accessing the AWS can also be used, and corresponding changes are required in `get_boto_client` present in    [boto_client.py](../src/cloud/aws/utils/boto_client.py)

6. In `sheets`, Provide the the creds for accessing google sheets either by storing creds in AWs secrets manager or hardcoding here.

7. In `outboundNotification`, currenly slack is only used. Provide the creds details either via AWsSecretManager or directly.           

    **NOTE**- To add any new `outboundNotification`, add like
    ```
        <new_channel>:
            use<new_channel>: True
            <new_channel>Name: 'infinity-bot'
            useAwsSecretManager: True
            secretName: 'infinity-slack-secrets'
            secretRegion: 'ap-southeast-1'
            #useAwsSecretManager: False
            #<new_chnanel_access_details>: ''

        Also with this corresponding code is required to be added in [notifications](../src/notifications/) and [alarm_checker.py](../src/alarm_checker.py)
    ```

8. At one time either AwsSecretManager can be used, or hardcoded values

## Format of secrets in AWS SecretManager

1. Slack: 
    ```
        SecretKey : <slack_channel_name>
        Secret Value : <slack_webhook_Url>
    ```

2. Sheets:
   ```
        SecretKey: <gsheets_service_account_credentials>
        Secret Value: <{   "type": "service_account",   "project_id": "<id_name>",   "private_key_id": "<private_key_id>",   "private_key": "<private_key>",   "client_email": "<email>",   "client_id": "<id>",   "auth_uri": "https://accounts.google.com/o/oauth2/auth",   "token_uri": "https://oauth2.googleapis.com/token",   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",   "client_x509_cert_url": "<client_cert_utrl>" }>
    ```

3. AWSAccess:
   ```
        SecretKey : ACCESS_KEY and SECRET_KEY
        Secret Value : <access-key and secrets-key>
    ```


**NOTE** - In case you are using AWSSecretManager, please add the access details for secret manager in [credentials](~/.aws/credentails) usder deafult profile.