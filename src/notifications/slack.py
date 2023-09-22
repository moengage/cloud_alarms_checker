import urllib3
import json

from cloud.aws.utils.secret import AWSSecretStoreSecret

def get_slack_webhook_for_channel(inputs):

    '''
        Getting the slack webhook Url from Aws Secret Manager
    '''
    
    webhookUrls = []

    if inputs['useAwsSecretManager'] == True:

        secret = AWSSecretStoreSecret( inputs['secretName'], inputs['secretRegion']).get()
        secret = json.loads(secret)
        for slackChannelName in inputs['slackChannelName']:
          webhookUrls.append(secret.get(slackChannelName))
        return webhookUrls
    else:
        return inputs['slackWebhookUrl']


def send_slack_notification(texts, inputs):
    
    '''
        Sending the spread sheet Url created and text generated to the slack channel
    '''

    if len(texts) == 0:
        return
    
    msg = f'\n'
    for text in texts:
        msg +=  f'{text}\n\n'
            
    print('Sending to slack...')

    # This will fetch the webhook Url from the AWs secret Manager
    webhook_urls = get_slack_webhook_for_channel(inputs)

    headers = {
        'Content-Type': 'application/json',
    }

    message = {
        "text": msg
    }

    for webhook_url in webhook_urls:
        http = urllib3.PoolManager()
        response = http.request(
            'POST', webhook_url, headers=headers, body=json.dumps(message))

        if response.status != 200:
            print('Failed to send slack', response.status, response.data)