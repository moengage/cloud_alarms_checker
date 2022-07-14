####################################################################################
#
# To create a docker container, Please update the following things:
#
#    1.  Update the username and password with you dockerhub account
#        ( You can modify it to use some other docker repo account as well)
#   
#    2. Update the docker repo path with required path
#
####################################################################################


#!/bin/bash
set -xe
docker login --username <user_name> --password <your_password>
docker build ../../../ -t <your_docker_repo>:latest
docker push <your_docker_repo>:latest