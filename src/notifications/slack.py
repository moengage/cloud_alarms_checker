import urllib3
import json

from cloud.aws.utils.secret import AWSSecretStoreSecret

def get_slack_webhook_for_channel(inputs):

    '''
        Getting the slack webhook Url from Aws Secret Manager
    '''

    if inputs['useAwsSecretManager'] == True:

        secret = AWSSecretStoreSecret( inputs['secretName'], inputs['secretRegion']).get()
        secret = json.loads(secret)
        return secret.get(inputs['slackChannelName'])
    
    else:

        return inputs['slackWebhookUrl']


def send_slack_notification(text, inputs):
    
    '''
        Sending the spread sheet Url created and text generated to the slack channel
    '''

    if not text:
        return
    print('Sending to slack...', text)

    # This will fetch the webhook Url from the AWs secret Manager
    webhook_url = get_slack_webhook_for_channel(inputs)

    headers = {
        'Content-Type': 'application/json',
    }

    message = {
        "text": text
    }

    http = urllib3.PoolManager()
    response = http.request(
        'POST', webhook_url, headers=headers, body=json.dumps(message))

    if response.status != 200:
        print('Failed to send slack', response.status, response.data)