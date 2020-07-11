#!/usr/bin/python
"""Gets IO instance specific information from IO. Note this data is mutable."""

# Import libraries
import json
import logging
from logging.config import fileConfig
import requests

# Print info to log.info in ./logs subdir, as well as to STDOUT
# See:
#      https://docs.python-guide.org/writing/logging
#      https://www.machinelearningplus.com/python/python-logging-guide
#      https://docs.python.org/2.4/lib/logging-config-fileformat.html
fileConfig('logging.ini')
logger = logging.getLogger('info')

# Local vars
folder_dict = {}
scanner_dict = {}
policies_dict = {}
tag_dict = {}

# Function to get the scan folders and ID's from IO, except 'Trash'
def get_folders(headers):
    """Get folder ID's from IO"""
    url = "https://cloud.tenable.com/folders"
    response = requests.request("GET", url, headers=headers)
    pretty_json = json.loads(response.text)
    data = (json.dumps(pretty_json, indent=2))
    data_dict = json.loads(data)

    for policies in data_dict:
        length = len(data_dict['folders'])
        counter = 0
        while counter < length:
            folder_id = data_dict['folders'][counter]['id']
            name = data_dict['folders'][counter]['name']
            if name == 'Trash':
                counter += 1
                continue
            else:
                counter += 1
                folder_dict[name] = folder_id
    logger.info(f'folder_dict is: \n{folder_dict}\n')

    return (folder_dict)
# End of function

# Function to get nessus scanner names and ID's from IO
def get_scanners(headers):
    """Get scanner ID's from IO"""
    url = "https://cloud.tenable.com/scanners"
    response = requests.request("GET", url, headers=headers)
    pretty_json = json.loads(response.text)
    data = (json.dumps(pretty_json, indent=2))
    data_dict = json.loads(data)

    for scanners in data_dict:
        length = len(data_dict['scanners'])
        counter = 0
        while counter < length:
            scanner_id = data_dict['scanners'][counter]['id']
            name = data_dict['scanners'][counter]['name']
            counter += 1
            scanner_dict[name] = scanner_id
    logger.info(f'scanner_dict is: \n{scanner_dict}\n')
    return (scanner_dict)
# End of function

# Function to get the user-defined scan policies and UUID's from IO
def get_policies(headers):
    """Get policy ID's from IO"""
    url = "https://cloud.tenable.com/policies"
    response = requests.request("GET", url, headers=headers)
    pretty_json = json.loads(response.text)
    data = (json.dumps(pretty_json, indent=2))
    data_dict = json.loads(data)

    for policies in data_dict:
        length = len(data_dict['policies'])
        counter = 0
        while counter < length:
            policy_id = data_dict['policies'][counter]['id']
            #cast id as a string so it can be concatendated with uuid
            policy_id = str(policy_id)
            uuid = data_dict['policies'][counter]['template_uuid']
            id_uuid_pair = ':'.join([policy_id, uuid])
            policy = data_dict['policies'][counter]['name']
            policies_dict[policy] = id_uuid_pair
            counter += 1
    logger.info(f'policies_dict is: \n{policies_dict}\n')
    return (policies_dict)
# End of function

# Function to get the UUID's for tags
def get_tags(headers):
    """Get tag data from IO for using in scans.ini"""
    url = "https://cloud.tenable.com/tags/values"
    response = requests.request("GET", url, headers=headers)
    pretty_json = json.loads(response.text)
    data = (json.dumps(pretty_json, indent=2))
    data_dict = json.loads(data)

    for values in data_dict:
        length = len(data_dict['values'])
        counter = 0
        while counter < length:
            uuid = data_dict['values'][counter]['uuid']
            tag_name = data_dict['values'][counter]['category_name']
            tag_value = data_dict['values'][counter]['value']
            tag_pair = ':'.join([tag_name, tag_value])
            tag_dict[tag_pair] = uuid
            counter += 1
    logger.info(f'tag_dict is: \n{tag_dict}\n')
    return (tag_dict)
# End of function

def main(access_key, secret_key):
    """Main function to get IO information"""
    logger.info('Running the info.py script\n')

    # Global var
    global headers

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'x-apikeys': f"accessKey={access_key};secretKey={secret_key}"}
    get_folders(headers)
    get_scanners(headers)
    get_policies(headers)
    get_tags(headers)

    logger.info('info.py script finshed execution')
    print ('\n  See "log.info" in the logs subdirectory for script output\n')

    # Return paramters for use in create.py so we don't have to duplicate
    # API call code there.
    return(folder_dict, scanner_dict, policies_dict, tag_dict)

if __name__ == '__main__':
    print ('\n  Do not execute this script directly.')
    print ('  Instead, execute chain.py using an argument.' \
          'Run "./chain.py --help" to see usage info.\n')
    print ('  Exiting...\n')
    exit()
