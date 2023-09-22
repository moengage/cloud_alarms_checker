from cloud.aws.utils.constants import MANDATORY_ACTION_TYPES, ResourceType
from cloud.aws.utils.utils import get_alarm_link

def write_to_spreadsheet(spreadsheet_writer, resource_class, active_resources, region_unmonitored_resources_map,
                         regional_resource_type_alarm_action_map, business_team_map, sns_topic_subscription_map):

    '''
        This will create the spread sheet and write the header row in the format of  
        'Region', 'Resource Type' 'Business', 'Team', 'Service', 'SubService', 'Reason', 'Alarm'

    '''

    # Adding Region And Resource type in header
    header_row = [ 'DC_NAME', resource_class.ACTIVE_RESOURCE_TYPE ]

    # If SUPPRESS_ON_ANY_METRIC variale is set, then one more extra field is appended
    if not resource_class.SUPPRESS_ON_ANY_METRIC:
        header_row.append('Missing alarm metrics')

    # Adding other fields in the header
    header_row.extend([ 'Business', 'Team', 'Service', 'SubService', 'Reason', 'Alarm'])

    # Creating the sheet for a specific resource type in the spread sheet with header row defined above.
    sheet = spreadsheet_writer.create_sheet( resource_class.VERBOSE_NAME, header_row)

    # Creating more rows based on the details obtained from the map, like region name, resource_name etc.
    rows = get_rows_from_region_unmonitored_resources_map( region_unmonitored_resources_map, resource_class, business_team_map)


    rows.extend( get_rows_from_alarm_action_map( resource_class, active_resources, regional_resource_type_alarm_action_map,
                                                 region_unmonitored_resources_map, business_team_map, sns_topic_subscription_map))

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
            if not resource_class.SUPPRESS_ON_ANY_METRIC:
                row.append(', '.join(metrics))
            
            # Fetching other information and storing in row.
            row.extend([
                business,
                business_team_map.get(business, ''),
                aws_resource.RESOURCE_TAGS_MAP[resource].get('Service', ''),
                aws_resource.RESOURCE_TAGS_MAP[resource].get('SubService', ''),
                reason, alarm
            ])
            rows.append(row)

    return rows


def get_rows_from_alarm_action_map(resource_class, active_resources, regional_resource_type_alarm_action_map, region_unmonitored_resources_map,
                                   business_team_map, sns_topic_subscription_map, text_format=False):

    '''
        This will fill remaining information in the sheet, like reason for unmonitoring and alarm etc.
    '''

    rows = []
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
            # If alarm dont contain the SNS topic attached to it, then correspondinf reason will be created
            if missing_action_types:
                verbose_missing_action_types = ', '.join(missing_action_types).upper() 
                reason = f'No {verbose_missing_action_types} topic associated'
            
            # If there is no endpoint in the SNS present, tehn corresponding reason is created.
            else:
                if 'sns' in action_types:
                    has_sns_subscription = False

                    for alarm_action in alarm_actions:
                        if alarm_action in sns_topic_subscription_map[region]:
                            has_sns_subscription = True
                            break

                    if has_sns_subscription:
                        continue
                    else:
                        reason = 'SNS topic is missing Endpoints'  # noqa: E501

            if not reason:
                continue
            
            # Finding teh alarm link for all those alarm which are associted with resouves and dont have SNS topic
            alarm_link = get_alarm_link(alarm_name, region)

            row = [region, resource_name]
            if not resource_class.SUPPRESS_ON_ANY_METRIC:
                row.append(metric_name)
                
            try:
                tags = aws_resource.RESOURCE_TAGS_MAP[resource_name]
            except KeyError:
                print("KeyError for ", resource_name)
            business = tags.get('Business', '').lower()

            alarm = alarm_name
            if not text_format:
                alarm = f'=HYPERLINK("{alarm_link}","{alarm_name}")'

            row.extend([
                business,
                business_team_map.get(business, ''),
                tags.get('Service', ''),
                tags.get('SubService', ''),
                reason, alarm])

            rows.append(row)

    return rows