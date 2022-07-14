<p align="center"><strong>Cloud Alarms Checker</a></strong></p>  

--------------------------------------------------------------------------------------------------------------------------------------

## What is Alarm Checker ?

This project is created to identify whether alarms and their corresponding actions are associated to the cloud resources or not.

For example, In case of AWS, this project is helpful in dentifying whether a SQS queue associates with any cloudwatch alarm or not. If it is associated then it is also checked whether any SNS topic is attached with some endpoint to it or not.

## UseCases and Features

1. Helps in identifying the resources not having alarms.
2. Can check for any number of region by simply changing in inputs file.
3. Easy to read google sheet is provided as an output, which can be sent out to via slack( or any channel with minimal code chnages)
4. Proper templating is provided to add any new resource
5. It is independent of cloud, and easily a new cloud resources can be introduced.

As a result of these scripts, a well classified tabular sheet is obtained containing all the information 
1. Region of the resource where it is present
2. Name of the resource
3. Creation time of the resource
4. Buisness, Service and Subserice name of the org, of which it is a part
5. If alarms are not present then a proper Description like `No Alarms are Present`
6. If alarms are present and no notification endpoint is provided, then proper description like `No Notification channel is attached to alarm` 

Also, to exempt any resource to be checked, it is suggested to attach a specific tags to them. 
For example, `"Monitor" : False` tag can be used and defined inside ../inputs/*yml to let the script know that any resource with this tag are exempted.

## Documentaions

1. To know more about the architechture, refer [Architecture.md](docs/Architecture.md)

2. To know more about on how to use the script, refer [How_To_Use.md](docs/How_To_Use.md)

3. To know more about on how to deploy the scripts in production environment, refer [Deployment.md](deployments/Readme.md)

## Contributions

To Contribute in the project, refer 
   1. [Developing.md](docs/Developing.md) 
   2. [Contributing.md](docs/Contributing.md)
   3. [Reviewing.md](docs/Reviewing.md)
   4. [Changelog.md](docs/Changelog.md)

   
## Resources

To know more about the policies, refer to [Code_of_Conduct.md](docs/Code_Of_Conduct.md)

--------------------------------------------------------------------------------------------------------------------------------------
<p align="center">Developed by <strong><a href="https://moenagage.com">MoEngage Team</a></strong></p>
<p align="center"> For any queries plaese opensource@moenagage.com </p>

                           
