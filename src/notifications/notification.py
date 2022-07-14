from notifications.slack import *

def send_notification(alert_message, inputs):
    
    if inputs['outboundNotification']['slack']['useSlack'] == True:
        send_slack_notification(alert_message, inputs['outboundNotification']['slack'])
    
    else:
        raise Exception("Please add code for some other notification channel like mail, teams etc")