import boto3                       

def return_boto_client_sns(region):
    return boto3.client("sns", region_name=region)

def check_sns_validity(integration_id_list,region,sns_arn):

    boto_client = return_boto_client_sns(region)
    result = ""
    try:
        response = boto_client.list_subscriptions_by_topic(
                                                    TopicArn=sns_arn)
        
        for subcription in response['Subscriptions']:
            if (subcription['Protocol'] == 'https' ) and ( 'https://events.pagerduty.com/integration' in subcription['Endpoint']):
                url = subcription['Endpoint']
                integration_id = url.split("/")[-2]
                if integration_id in integration_id_list:
                    result="Valid Alarm"
                    break
                else:
                    result="Not Valid Alarm - False IntegrationKey"
            else:
                result="Not Valid Alarm - No PDEndpoint"
    except:
        result = "Not Valid SNS"
        
    return result