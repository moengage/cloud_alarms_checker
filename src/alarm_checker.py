#!/usr/local/bin/python3

import datetime
import click

from dateutil import tz

from utils.team_map import *
from utils.utils import *
from notifications.notification import send_notification

from outputs.sheets import *

from cloud.aws.aws_main import aws_alarm_checker
from cloud.azure.azure_main import azure_alarm_checker

@click.command()
@click.option("--inputs", required=True, help="Comma Separated Input Yaml file for each cloud  - <path of yaml file>")
def main(inputs):

    '''
        Main Function to check for all unmonitored resources present in AWS.
        This will store all those resources in spreadsheet and send the sheet url to slack channel

    '''
    
    alert_message = []
    for input in inputs.split(','):
        

        set_input(input)

        # This will read all the inputs provided in input_yaml
        yaml_inputs = yaml_reader()

        # Fetching the environment
        env = yaml_inputs['env']
        
        dcs = []
        for dc in yaml_inputs['env_region_map']:
            dcs.append(dc)
            
        cloud = yaml_inputs['cloud'] 
        
        if cloud == 'aws':
            
            print('##################################################\n')
            print('RUNNING ALARM CHECKER FOR AWS')
            print('##################################################\n')
            
            # Creating spreadsheets
            aws_spreadsheet_writer = create_sheets(cloud, env, yaml_inputs)
            
            # Geting buisness team map from consul host
            business_team_map = get_business_team_map(yaml_inputs['buisness_team_map'])
            
            has_aws_unmonitored_resources = aws_alarm_checker( env, yaml_inputs, business_team_map, dcs, aws_spreadsheet_writer)
            if has_aws_unmonitored_resources:
                aws_spreadsheet_writer.autoresize_spreadsheet()
                aws_spreadsheet_writer.spreadsheet.del_worksheet( aws_spreadsheet_writer.spreadsheet.worksheets()[0])

                sheet_link = aws_spreadsheet_writer.sheet_url
                alert_message.append( f'Unmonitored `{env}` `{cloud}` resources - {sheet_link}')

        elif cloud == 'azure':
            
            
            print('##################################################\n')
            print('RUNNING ALARM CHECKER FOR AZURE')
            print('##################################################\n')
            
            azure_spreadsheet_writer = create_sheets(cloud, env, yaml_inputs)
            has_azure_unmonitored_resources = azure_alarm_checker( env, yaml_inputs,azure_spreadsheet_writer)
            
            if has_azure_unmonitored_resources:
                azure_spreadsheet_writer.autoresize_spreadsheet()
                azure_spreadsheet_writer.spreadsheet.del_worksheet( azure_spreadsheet_writer.spreadsheet.worksheets()[0])

                sheet_link = azure_spreadsheet_writer.sheet_url
                alert_message.append( f'Unmonitored `{env}` `{cloud}` resources - {sheet_link}')
            
        else:
            raise Exception("Please use correct cloud, as this is not supported %s", cloud )
    
    
    send_notification( alert_message)
    
if __name__ == '__main__':
    main()
