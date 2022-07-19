#!/usr/local/bin/python3

import datetime
import click

from dateutil import tz

from utils.team_map import *
from utils.utils import *
from notifications.notification import send_notification

from outputs.sheets import *

from cloud.aws.aws_main import aws_alarm_checker

@click.command()
@click.option("--input", required=True, help="Input Yaml file - <path of yaml file>")
def main(input):

    '''
        Main Function to check for all unmonitored resources present in AWS.
        This will store all those resources in spreadsheet and send the sheet url to slack channel

    '''

    set_input(input)

    # This will read all the inputs provided in input_yaml
    yaml_inputs = yaml_reader()
    print(input)

    # Fetching the environment
    env = yaml_inputs['env']

    # Fetching list of regions based on the environment selected.
    regions = yaml_inputs['regions']

    cloud = yaml_inputs['cloud'] 

    # Creating spreadsheets 
    spreadsheet_writer = create_sheets(cloud, env, yaml_inputs)

    # Geting buisness team map from consul host
    business_team_map = get_business_team_map(yaml_inputs['buisness_team_map'])

    if cloud == 'aws':
        has_unmonitored_resources = aws_alarm_checker( env, yaml_inputs, business_team_map, regions, spreadsheet_writer)

    else:
        raise Exception("Please add the code for %s", cloud )

    if has_unmonitored_resources:
       
        # After Filling the spreadsheet with all the information, it is resized and pruned and 
        # then its link is sent to the required slack channel

        spreadsheet_writer.autoresize_spreadsheet()
        spreadsheet_writer.spreadsheet.del_worksheet( spreadsheet_writer.spreadsheet.worksheets()[0])

        sheet_link = spreadsheet_writer.sheet_url
        alert_message = ( f'Unmonitored `{env}` `{cloud}` resources - {sheet_link}')
      
        send_notification( alert_message, yaml_inputs)
    
if __name__ == '__main__':
    main()
