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
├── README.md                  -> Top Level README, explaining the use of project
|__ LICENSE.md                 -> MIT License
|__ VERSION                    -> Version file containing latest tag information
├── deployments                -> Copntains the methods on how to deploy in production environment
│   └── prod
│       ├── docker
│       │   ├── Dockerfile
│       │   └── build_and_push_to_repo.sh
|       |   |__ README.md      -> Explains the docker environment
│       └── kubernetes
|           |__<new_cloud>
|           |__aws
│           	└── cronjob.yaml
|           	|__ README.md      -> Explains the kubernetes environment
├── docs                       -> Several documents to explain the project
│   ├── ARCHITECTURE.md        -> Gives the directory structure details and how to use and contribute details
│   ├── CHANGELOG.md           -> Defines the info, on the tags, after making any changes
│   ├── CODE_OF_CONDUCT.md     -> Code of conduct to contribute and use the project
│   ├── CONTRIBUTING.md        -> Contributing Guidelines on how to raise PR etc.
│   ├── DEVELOPING.md          -> Developing Guidelines
│   ├── HOW_TO_USE.md          -> How to use and run the project in local environment
│   └── REVIEWING.md           -> Reviweing guidelines
├── inputs
|      |__aws                 
│          ├── README.md        -> README explining on how to use yaml file       
│          └── aws_inputs.yaml  -> Yaml inputs required for aws
├── requirements.txt
└── src
    ├── __init__.py
    ├── alarm_checker.py         -> Main Src File to check the alarms
    ├── cloud
    |   |__<new_cloud>           -> Add folder and required scripts if adding new cloud
    │   └── aws                  -> AWS specific files
    │       ├── README.md        -> Explaining what is being done for AWS
    │       ├── __init__.py
    │       ├── aws_main.py      -> Main file for aws called from `../alarm_checker.py'
    │       ├── resource_classes 
    │       │   ├── README.md    -> README explaining on how to add new resource
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
    │   ├── spreadsheet.py   -> Creating the google spreadsheet
    │   └── writer.py        -> Writing to spreadsheet created
    └── utils
        ├── team_map.py
        └── utils.py

```