from cloud.aws.utils.constants import MANDATORY_ACTION_TYPES, ResourceType
from cloud.aws.utils.utils import get_alarm_link
from cloud.aws.utils.sns_validity import check_sns_validity


def write_to_spreadsheet(spreadsheet_writer, resource_class, active_resources, region_unmonitored_resources_map,
                         regional_resource_type_alarm_action_map, business_team_map, sns_topic_subscription_map,integration_id_list, yaml_inputs):

    '''
        This will create the spread sheet and write the header row in the format of  
        'Region', 'Resource Type' 'Business', 'Team', 'Service', 'SubService', 'Reason', 'Alarm'

    '''

    # Adding Region And Resource type in header
    header_row = [ 'DC_NAME', resource_class.ACTIVE_RESOURCE_TYPE ]

    header_row.extend([ 'Business', 'Team', 'Service', 'SubService'])

    # If SUPPRESS_ON_ANY_METRIC variale is set, then one more extra field is appended
    if not resource_class.SUPPRESS_ON_ANY_METRIC:
        header_row.append('Missing alarm metrics with reason')
    
    if not resource_class.SUPPRESS_ON_ANY_METRIC:
        header_row.append('Alarm')

    # Creating the sheet for a specific resource type in the spread sheet with header row defined above.
    sheet = spreadsheet_writer.create_sheet( resource_class.VERBOSE_NAME, header_row)

    # Creating more rows based on the details obtained from the map, like region name, resource_name etc.
    first_rows = get_rows_from_region_unmonitored_resources_map( region_unmonitored_resources_map, resource_class, business_team_map)

    second_rows= get_rows_from_alarm_action_map( resource_class, active_resources, regional_resource_type_alarm_action_map,region_unmonitored_resources_map, business_team_map, sns_topic_subscription_map,integration_id_list, yaml_inputs)
    rows=[]

    # below we are formatting the column of the sheet based on the individual result we got from above line 31 and 33
    # we are checking if the resouce name and dc in list of rows of first row match with resouce name and dc in list of rows of second row, then update the data of 'Missing alarm metrics with reason' having both row first and row second detail.
    
    for index1 in first_rows:
        found = False
        for index2 in second_rows:
            if index1[0] == index2[0] and index1[1] == index2[1]:
                # Joining two relevant columns with a new line separator
                rows.append([index1[0], index1[1], index1[2], index2[3], index2[4],
                                index2[5],index1[6]+"\n" + index2[6], index2[7]])
                found = True
                break
        if not found:
            rows.append(index1)

    sheet.append_rows(rows, value_input_option='USER_ENTERED')
    sheet.sort(
        (5, 'asc'), (8, 'asc'), (5, 'asc'), (1, 'asc'),
        range='A2:Z1000')

    return len(rows)

def get_rows_from_region_unmonitored_resources_map( region_unmonitored_resources_map, resource_class, business_team_map):

    '''
        This will create the rows with full info of all unmonitored resources.ß
    '''

    
    rows = []
    # Variable denoting that no alarm are present.
    reason = "No Alarm present"

    # Alarm link will always be empty. This is just a placeholder
    alarm = ''

    # Fetching region, (resource_type, resources_names) from the map
    for region, (aws_resource, unmonitored_resources) in region_unmonitored_resources_map.items():

        for resource, metrics in unmonitored_resources.items():
            # Fetching the business name
            business = aws_resource.RESOURCE_TAGS_MAP[resource].get( 'Business', '').lower()

            row = [region, resource]
                
            # Fetching other information and storing in row.
            row.extend([
                business,
                business_team_map.get(business, ''),
                aws_resource.RESOURCE_TAGS_MAP[resource].get('Service', ''),
                aws_resource.RESOURCE_TAGS_MAP[resource].get('SubService', '')
            ])

            if not resource_class.SUPPRESS_ON_ANY_METRIC:
                row.append(f'----{reason}\n'.join(metrics))
            row[-1]=row[-1]+f"----{reason}"
                
            rows.append(row)
    return rows

def get_rows_from_alarm_action_map(resource_class, active_resources, regional_resource_type_alarm_action_map, region_unmonitored_resources_map,
                                   business_team_map, sns_topic_subscription_map,integration_id_list, yaml_inputs,text_format=False ):

    '''
        This will fill remaining information in the sheet, like reason for unmonitoring and alarm etc.
    '''

    rows = []
    rows_return=[]
    active_resource_names = []
    resource_type = resource_class.ACTIVE_RESOURCE_TYPE
 
    for resource_arn in active_resources:

        # fetching the name of resources from thier arn/ids
        resource_name = resource_arn.split(':')[-1]

        if resource_type == ResourceType.TARGET_GROUP:
            resource_name = resource_name.split('/')[1]
        elif resource_type == ResourceType.LOAD_BALANCER:
            resource_name = resource_name.split('/')[2]

        active_resource_names.append(resource_name)

    for region, resource_map in regional_resource_type_alarm_action_map.items():

        # fetching resources for a specific region 
        aws_resource = region_unmonitored_resources_map[region][0]
        
        # Fetching resource name, alarm name, metruc name etc from the map
        for resource_name, alarm_name, metric_name, action_types, alarm_actions in resource_map[resource_type]: 
            missing_action_types = set(MANDATORY_ACTION_TYPES) - set(action_types) 
            
            # Skip inactive resources
            if resource_name not in active_resource_names:
                continue

            autoscaling_alarm = False
            for action in action_types:

                if 'autoscaling' in action:
                    autoscaling_alarm = True

            if autoscaling_alarm:
                continue

            
            reason = ''
            # If alarm doesn't contain the SNS topic attached to it, then corresponding reason will be created
            if missing_action_types:
                verbose_missing_action_types = ', '.join(missing_action_types).upper() 
                reason = f'No {verbose_missing_action_types} topic associated'

            # If there is no endpoint in the SNS present, then corresponding reason is created.
            else:
                if 'sns' in action_types:
                    has_sns_subscription = False
                    valid_subscription = False

                    for alarm_action in alarm_actions:
                        if alarm_action in sns_topic_subscription_map[region]:
                            has_sns_subscription = True
                        subscription_arn = alarm_action
                        
                        region_name=yaml_inputs['env_region_map'][region]['region']
                        pd_integration_check=yaml_inputs['env_region_map'][region]['pd_integration_key_check']

                        # Getting the boolean value from the input file to check, if the user wants to validate the sns validity else simply return "valid Alamr"
                        
                        if pd_integration_check == True:
                            # This will check the validity of the sns topic by checking the pagerduty integration key
                            subscription_info = check_sns_validity(integration_id_list,region_name,subscription_arn)
                        else:
                            subscription_info = "Valid Alarm"       
                        if subscription_info == "Valid Alarm":
                            valid_subscription = True
                        break

                    if has_sns_subscription and valid_subscription:
                        continue
                    elif has_sns_subscription and not valid_subscription:
                        reason = "SNS topic has invalid HTTP(S) - PD endpoint subscription"                
                    else:
                        reason = 'SNS topic has missing Endpoints'

            if not reason:
                continue
            
            row = [region, resource_name]
            try:
                tags = aws_resource.RESOURCE_TAGS_MAP[resource_name]
            except KeyError:
                print("KeyError for ", resource_name)

            business = tags.get('Business', '').lower()
            row.extend([
                business,
                business_team_map.get(business, ''),
                tags.get('Service', ''),
                tags.get('SubService', '')
               ])


            if not resource_class.SUPPRESS_ON_ANY_METRIC:
                row.append(metric_name)

            row[-1]=row[-1]+f"----{reason}"
                
            alarm = alarm_name
            alarmlink=f'https://console.aws.amazon.com/cloudwatch/home?region={region_name}#alarmsV2:alarm/{alarm}'

            if not resource_class.SUPPRESS_ON_ANY_METRIC:
                row.append(alarmlink)
            rows.append(row)
    
    # updating the 'Missing alarm metrics with reason' and 'Alarm' column by adding all the metric value and alarm reason in a single column, if multiple metric and alarm found for the same resource.

    if len(rows)>1:
        for item in rows:
            found = False
            for l in rows_return:
                if item[0] == l[0] and item[1] == l[1]:
                    # Joining two relevant columns with a new line separator
                    l[-1] += "\n" + item[-1]
                    l[-2] += "\n" + item[-2]
                    found = True
                    break
            if not found:
                rows_return.append(item)
    else:
        rows_return=rows
        
    return rows_return