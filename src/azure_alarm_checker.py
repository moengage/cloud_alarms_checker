#!/usr/local/bin/python3

import datetime
import click
import sys

from dateutil import tz

from utils.team_map import *
from utils.utils import *
from notifications.notification import send_notification

from outputs.sheets import *

from cloud.azure.azure_main import azure_alarm_checker

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

    # Fetching the environment
    env = yaml_inputs['env']

    cloud = yaml_inputs['cloud'] 

    # Creating spreadsheets
    spreadsheet_writer = create_sheets(cloud, env, yaml_inputs)

    if cloud == 'azure':
        has_azure_unmonitored_resources = azure_alarm_checker( env, yaml_inputs,spreadsheet_writer)

    else:
        raise Exception("Please use the code for %s", cloud )

    if has_azure_unmonitored_resources:
       
        # After Filling the spreadsheet with all the information, it is resized and pruned and 
        # then its link is sent to the required slack channel

        spreadsheet_writer.autoresize_spreadsheet()
        spreadsheet_writer.spreadsheet.del_worksheet( spreadsheet_writer.spreadsheet.worksheets()[0])

        sheet_link = spreadsheet_writer.sheet_url
        alert_message = ( f'Unmonitored `{env}` `{cloud}` resources - {sheet_link}')
      
        send_notification( alert_message, yaml_inputs)
    
if __name__ == '__main__':
    main()
