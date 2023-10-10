from notifications.slack import *
import yaml
from yaml.loader import SafeLoader

def send_notification(alert_message):
        
    with open('/Users/priyasharma/Documents/Tasks/CloudALrmChecker/cloud_alarms_checker/inputs/notification.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)

    if data['outboundNotification']['slack']['useSlack'] == True:
        print("Slack send skipped")
        send_slack_notification(alert_message, data['outboundNotification']['slack'])
    
    else:
        raise Exception("Please add code for some other notification channel like mail, teams etc")