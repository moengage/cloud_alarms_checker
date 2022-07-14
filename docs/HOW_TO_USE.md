# How to Use the Cloud Alarms Checker

Following are the ways the ways to access the project:

### In Linux Machine
1. Clone the repository using    
    `git clone <repo_url`
2. Install the python3 in linux machine  
    ```
        For ex in ubuntu:
            apt-get update
            apt-get install python3-pip
    ```
3. Install the dependencies required by project by using [requirements.txt](../requirements.txt)  
    ` python3 -m pip install -r requirements.txt`
4. Edit the [inputs_yaml](../inputs/) file based on the instruction provided in Readme for a specific clud in `../inputs/<cloud>
5. Run the project   
    a. Manually
        ```
            cd src  
            python3 alarm_checker.py --input <input_file_path>
        ```  
    b. As a cron job in specific time interval


### In Docker Environment
1. Clone the repository using  
    `git clone <repo_url`
2. Install docker in you local environment
3. Run the [Dockerfile](../deployments/prod/docker/)
    ```
        cd deployments/prod/docker/  
        docker login --user <user_name> --password <password>  
        docker build -t . <tag>  
        docker images    ---> <Check whether Image is created or not>  
        docker run -it <name_of_container> <image_id> /bin/bash
    ```
    **NOTE** - You can upload to the docker hub using [script](../deployments/prod/docker/build_and_push_to_repo.sh)  
    ```  
        docker login  
        docker pull <image_tag>    
        docker images    ---> <Check whether Image is created or not>    
        docker run -it <name_of_container> <image_id> /bin/bash
    ```
4. Run the project  
    a. Manually
    ```  
        cd src  
        python3 alarm_checker.py --input <input_file_path>
    ```
    b. As a cron job in specific time interval


### In Kubernetes Environment

1. Edit the [cronJob.yaml](../deployments/prod/kubernetes/cronjob.yaml) with new namespace and docker image and cron Interval

2. In you kubernetes environment, run
    ```
        kubectl apply -f cronjob.yaml
    ```

**NOTE**- There can be other several depending upon the environment of user.