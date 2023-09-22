import requests
import json
import time
import sys
import os
import subprocess

run_query_api_version = '2020-04-01-preview'

PY3 = sys.version_info >= (3, 0, 0)

def execute_command(command, preserve_output=True, show_command=False, exit_on_error=False,
        show_output=False, process_stdout_color=None):
    os.environ["PYTHONUNBUFFERED"] = "1"
    if show_command:
        print('Executing command: %s' % command)
    kwargs = {}
    if PY3:
        kwargs['encoding'] = 'utf-8'
        kwargs['errors'] = 'replace'
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               shell=True, **kwargs)
    output = []
    while True:
        realtime_output = process.stdout.readline()
        if preserve_output:
            output.append(realtime_output.strip())
        if realtime_output == '' and process.poll() is not None:
            break
        if realtime_output and show_output:
            kwargs = {}
            if process_stdout_color:
                kwargs['fg'] = process_stdout_color
            print(realtime_output.strip(), **kwargs)
    if exit_on_error and process.returncode > 0:
        print('{} exited with {}'.format(command, process.returncode), fg='red')
        sys.exit(process.returncode)
    return process.returncode, output


def set_header(dc_map):
    
    tenant_id = dc_map["tenant_id"]
    client_id = dc_map["client_id"]
    client_secret = dc_map["client_secret"]
    
    credentials_info = f'az login --service-principal -u {client_id} -p {client_secret} --tenant {tenant_id}'

    execute_command(f'{credentials_info}',show_output=False )

    execute_command('az account get-access-token > ./access-token.json',show_output=False, show_command=False)
    
    execute_command('az logout')


def get_header():
    

    f = open(f'./access-token.json')
    execute_command('cat ./access-token.json')
    access_token = json.load(f)["accessToken"]

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    return headers

def get_resources_list(query, dc,  get_full_properties=False):

    subscription_id = dc["subscription_id"]
    
    headers = get_header()

    post_query_url = 'https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version={}'.format(run_query_api_version)

    data = {
        "subscriptions": [
            subscription_id
        ],
        "query": f'{query}'
    }

    response = requests.post(post_query_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:

        result = json.loads(response.content)

        if get_full_properties:
            return result['data']['rows']
        resource_list = [ row[0]  for row in result['data']['rows'] ]
        return resource_list

    elif response.status_code == 429:

        time.sleep(5)
        resource_list = get_resources_list()
        return resource_list

    else:

        print(response.content)
        print(response.status_code)
        sys.exit(1)