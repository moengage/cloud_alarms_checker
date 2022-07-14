# AWS Specific Alarms Checker

In case of AWS, this project is helpful in dentifying whether a SQS queue associates with any cloudwatch alarm or not. If it is associated then it is also checked whether any SNS topic is attached with some endpoint to it or not.

# Active Queue Definition
No.of messages sent are greater than 0 in the last 7 days.

# Active TG definition
No.of requests greater than 0 in the last 7 days.

# Active Elasticache definition
No.of get commands are greater than 0 in the last 7 days.

Owners todos
    - If any Active Infra doesn’t need monitoring, please introduce a tag with Key “Monitor” and value to be “False”

    - All the Infra which are active are expected to have mandatory Alarms mentioned in the Alarms SOPs

How will we identify the anomalies?
- Script can be run on the basis of cron job to check all the infra in system.

For every active Infra, we check (Algo)

1. If the mandatory Alarms are present or not. 
    Even if 1 of the mandatory alarm is not present, we will add the infra to the breaches list saying Alarms are missing and the description of the alert should have it. `- Description  - > No Alarm present`

2. If there are any alarms configured for a resource:

    - If none of the alarms has a SNS based alarm action, that resource should be considered under No Alarm present
    - If atleast one alarm has SNS based action, associated SNS topic should have at least one valid subscription. If none of the alarms has a valid SNS subscription, then we categorize it as SNS Subscription missing for alarm. The report should contain a column with the alarm link in this case.

NOTE: For adding any new infra refer [README.md](resource_classes/README.md).
