# How to Develop the project

Currently only aws cloud is suported in the project with some definite resources. 

## Architecture
Refer [ARCHITECTURE.md](./ARCHITECTURE.md)

## Adding new resource in AWS 
Refer [README.md](../src/cloud/aws/README.md)

## Adding new cloud
1. To add a new cloud like azure or gcp, creta the respective folders inside `../cloud directory` in the format of
```
cloud
    └── <new_cloud>
    ├── README.md
    ├── __init__.py
    ├── <new_cloud>_main.py
    ├── resource_classes
    │   ├── README.md
    │   ├── __init__.py
    │   ├── base.py
    │   ├── <resource_1>.py
    │   ├── <resource_2>.py
    │   └── template.py
    └── utils
        ├── alarms.py
        ├── <accessing the cloud>_client.py
        ├── constants.py
        ├── secret.py
        └── utils.py
```

2. Add the corresponding code to invoke the new cloud code in [alarm_checker.py](../src/alarm_checker.py)
3. Add the corresponding yaml input file with `spec.cloud: <new_cloud>` under `../inputs/<new_cloud>`


## Ading new notification channel
1. Add the corresponding script in `../notification`.
2. Add the corresponding code to invoke the new cloud code in [alarm_checker.py](../src/alarm_checker.py)
3. Add the corresponding inputs in `../inputs/<cloud>/*yaml` under `spec.outputNotifications.<new_channel>`

## Dependencies
Make sure, every new dependency are added in [Requirements.txt](../requirements.txt)

## Documentation
Please make sure that all the documentation present in `../docs/*.md` are updated after any development 

## Testing  and Use
1. To know how to use the scripts refer to [HOW_TO_USE.md](./HOW_TO_USE.md)
2. Make sure that proper testing is performed before raising the PR or mering the PRs
    a. Make sure the google sheet is preparing fine
    b. Make sure that sheet link is sent to slack channel correctly

## Adding or Changing Deployment method
1. Add any new deployment method in `../deployments/prod/<deployment_type>
2. Make sure you have aded proper steps in accessing the method in [README.md](./HOW_TO_USE.md)
3. If you are making changes in existing deployment methods, make sure the proper testing is done and keep it as generic as possible.

## Contributing Guidelines
Refer [Contributing.md](./Contributing.md) for more details

## Reviewing Guidelines
Refer [Reviewing.md](./Reviewing.md) for more details

## Merging guidelines 
After every merge, follow the steps present in [CHANGELOG.md](./CHANGELOG.md) to create new tag

## Queries
Please mail to opensource@moengage.com for any query and issue/feature request

**IMP NOTE** - Make sure the code remains generic as much as possible.
