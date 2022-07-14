# Architecture

Following is the architecture

```                                                                                            
    [UserInputs](../inputs) 
        |
    [alarms_checker.py](../src/alarm_checker.py) 
        |
    secretsAcccess 
        |
    Checking for resources whether alarm are present or not for a cloud 
        |
    Creating Google sheet and writing the anamolies into it 
        |
    Sending the sheet link to slack

```

## Directory Structure

```
.
├── README.md                  -> Top Level Readme, explaining teh use of project
├── deployments                -> Copntains the methods on how to deploy in production environment
│   └── prod
│       ├── docker
│       │   ├── Dockerfile
│       │   └── build_and_push_to_repo.sh
|       |   |__ Readme.md      -> Explains the docker environment
│       └── kubernetes
|           |__<new_cloud>
|           |__aws
│           	└── cronjob.yaml
|           	|__ Readme.md      -> Explains the kubernetes environment
├── docs                       -> Several documents to explain the project
│   ├── Architecture.md        -> Gives the directory structure details and how to use and contribute details
│   ├── Changelog.md           -> Defines teh info, on the tags, after making any changes
│   ├── Code_Of_Conduct.md     -> Code of conduct to contribute and use the project
│   ├── Contributing.md        -> Contributing Guidelines on how to raise PR etc.
│   ├── Developing.md          -> Developing Guidelines
│   ├── How_To_Use.md          -> How to use and run the project in local environment
│   └── Reviewing.md           -> Reviweing guidelines
├── inputs
|      |__aws                 
│          ├── Readme.md        ->  Readme explining on how to use yaml file       
│          └── aws_inputs.yaml  -> Yaml inputs required for aws
├── requirements.txt
└── src
    ├── __init__.py
    ├── alarm_checker.py         -> Main Src File to check the alarms
    ├── cloud
    |   |__<new_cloud>           -> Add folder and required scripts if adding new cloud
    │   └── aws                  -> AWS specific files
    │       ├── Readme.md        -> Explaining what is being done for AWS
    │       ├── __init__.py
    │       ├── aws_main.py      -> Main file for aws called from `../alarm_checker.py'
    │       ├── resource_classes 
    │       │   ├── Readme.md    -> Readme explaining on how to add new resource
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   ├── elasticache_redis.py
    │       │   ├── load_balancer.py
    │       │   ├── sqs_queue.py
    │       │   ├── target_group.py
    │       │   └── template.py    -> Template file to give idea on how to add new resource
    │       └── utils
    │           ├── alarms.py      -> Alarms specific file
    │           ├── boto_client.py -> Creating a AWS boto client
    │           ├── constants.py
    │           ├── secret.py      -> Accessinhg the AWS secret Manager if required
    │           └── utils.py
    ├── notifications
    │   └── slack.py        -> Sending final output to slack
    |   |__ <new_notification_channel.py> -> Addinhg a new notification channel if required
    ├── sheets
    │   ├── spreadsheet.py   -> Creating teh google spreadsheet
    │   └── writer.py        -> Writing to spreadsheet created
    └── utils
        ├── team_map.py
        └── utils.py

```
