import json
import pypd
import requests
import concurrent.futures
from cloud.aws.utils.secret import AWSSecretStoreSecret

# Function to fetch all teams and their associated services
def get_teams_and_services():
    
    # Fetch all the teams in the organization
    teams = pypd.Team.find()
    team_services = []
    
    # Iterate over each team and fetch its services
    for team in teams:
        team_name = team['name']
        team_id = team['id']
        team_services.append({
            'team': team_name,
            'services': []
        })
        
        # Fetch the services associated with each team
        try:
            services = pypd.Service.find(team_ids=[team_id])
        except Exception as e:
            print(f'Error occurred while fetching services for team ID {team_id}: {e}')
            continue
        
        if len(services) == 0:
            continue
        
        for service in services:
            service_name = service['name']
            service_id = service['id']
            
            # Add the service to the list of team services
            team_services[-1]['services'].append({
                'name': service_name,
                'id': service_id
            })
    
    return team_services

def get_integration_details(service_id, integration_id, api_key):
    
    # Set the PagerDuty API endpoint and request parameters
    url = f'https://api.pagerduty.com/services/{service_id}/integrations/{integration_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Token token={api_key}',
        'Content-Type': 'application/json'
    }

    # Execute the API call
    response = requests.get(url, headers=headers)

    # Check if the API call was successful (status code 200)
    if response.status_code == 200:
        print('API call was successful.')
    else:
        print('An error occurred while making the API call.')

    # Print the API response content
    json_response=response.content.decode()

    # Parse the JSON response
    parsed_response = json.loads(json_response)

    # Extract the value of the integration_key field
    integration_key = parsed_response['integration']['integration_key']

    return integration_key

# Function to fetch integration id for a service
def get_service_integration(service_id):
    
    api_key=get_pd_api_key()
    try:
        # Fetch the service by ID
        service = pypd.Service.fetch(service_id)
        
        # Iterate over each integration of the service and print its ID
        if service['status'] == 'active':
            integration_keys = []
            for integration in iter(service.integrations()):
                integration_id = integration["id"]
                integration_key = get_integration_details(service_id, integration_id, api_key)
                if integration_key is not None:
                    integration_keys.append(integration_key)
            return integration_keys
            
        elif service['status'] == 'disabled':
            print(service_id, "is disabled")
            return []
        else:
            print(f'{service_id} is neither active nor disabled')
            return []
            
    except Exception as e:
        print(f'Error occurred while fetching service: {e}')
        return None

def get_integrations_for_team(team):
    team_name = team['team']
    services = team['services']
    
    if len(services) == 0:
        print(f'No services found for team {team_name}.')
        return []
    
    print(f'Team: {team_name}')
    
    integration_key_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(services)) as executor:
        future_to_service = {}
        for service in services:
            service_name = service['name']
            service_id = service['id']
            
            # Print the service name and ID
            print(f'- Service: {service_name} ({service_id})')

            # Schedule the function to run in a different thread
            future = executor.submit(get_service_integration, service_id)
           
            # Map the service name to the future object for later retrieval
            future_to_service[future] = service_name
           
        for future in concurrent.futures.as_completed(future_to_service):
            # Get the name of the service associated with the future object
            service_name = future_to_service[future]

            # Get the list of integration keys for the service from the future object
            integration_keys = future.result()

            # Append the integration keys to the global list
            if integration_keys is None:
                print(f'-- Failed to retrieve integration keys for service {service_name}')
                integration_keys = []

            # Append the integration keys to the global list
            integration_key_list.extend(integration_keys)
            print(f'-- Retrieved {len(integration_keys)} integration keys for service {service_name}')
   
    return integration_key_list

def get_pd_api_key():
    apikey_info = AWSSecretStoreSecret( 'pagerduty_api_key','ap-southeast-1').get()
    apikey = json.loads( apikey_info)['pagerduty_api_key']
    return apikey

def run_integration():
    pypd.api_key = get_pd_api_key()
    integration_key_list=[]

    team_services=get_teams_and_services()
    for team in team_services:
        team_integration_keys = get_integrations_for_team(team)
        integration_key_list.extend(team_integration_keys)

    print(f'Total integration keys: {len(integration_key_list)}')

    return integration_key_list