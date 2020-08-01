#!/usr/bin/python
"""Creates scans using scans.ini config file when called by chain.py"""
# Import modules
import json
import re
import time
import sys
import configparser
import logging
from logging.config import fileConfig
import requests

# Print info to log.chain in ./logs subdir, as well as to STDOUT
# See logging.ini for logging configuration
# See:
#      https://docs.python-guide.org/writing/logging
#      https://www.machinelearningplus.com/python/python-logging-guide
#      https://docs.python.org/2.4/lib/logging-config-fileformat.html
fileConfig('logging.ini')
logger = logging.getLogger('create')

# Function to create scans using dictionaries for folders, scanners and policies
def create_scans(policy_uuid, scan_name, description, policy_id, folder_id,
                 scanner_id, launch, scan_targets, email, tag_targets, headers):
    """Main function to create scans in IO"""
    scan_flag = 0

    # At least one, or both, of scan_targets and tag_targets must be defined
    if scan_targets != '' or tag_targets != '':
        payload_str = f'"uuid":"{policy_uuid}","settings":{{"name":"{scan_name}", \
                       "description":"{description}", "policy_id":{policy_id}, \
                       "folder_id":{folder_id}, "scanner_id":{scanner_id}, \
                       "launch":"{launch}", "emails":"{email}", \
                       "acls":[{{"permissions":0,"owner":1, \
                       "type":"default"}}], \
                       "text_targets":"{scan_targets}", \
                       "tag_targets":[{tag_targets}]}}'
        payload_str = '{' + payload_str +'}'
        payload = f'{payload_str}'
        scan_flag = 1

    elif scan_targets == '' and tag_targets == '':
        logger.info(f'ERROR on creation of "{scan_name}". Both text_targets ' \
        'and tag_targets are blank in scans.ini file. At lest one must be ' \
        'declared. Fix the scans.ini definition for this scan and run the ' \
        'scan creation again. Exiting the create_scans function...')
        exit()

    else:
        logger.info('UNKOWN ERROR. Exiting')
        exit()

    if scan_flag == 1:
        logger.info(f'Creating "{scan_name}" scan')
        # Replace multiple spaces with just one for
        # readability in STDOUT and logs
        payload = re.sub('\s+', ' ', payload)
        logger.info(f'Payload is: {payload}')

        try:
            url = "https://cloud.tenable.com/scans"
            response = requests.request("POST", url, data=payload, headers=headers)
            response.raise_for_status()
            logger.info(f'The scan \"{scan_name}\" has been created')
            # A delay is not required, but is good to tread lightly on the API
            # and avoice rate limiting isues. See the following URL:
            # https://developer.tenable.com/docs/rate-limiting
            logger.info('Pausing for 1 second before the next API call....')
            time.sleep(1)

        except requests.HTTPError as e:
            logger.info(f'ERROR - {e}')
            sys.exit()
# End function

# main function
def main(access_key, secret_key, folder_dict, scanner_dict, policies_dict, \
         tag_dict):
    """Main function in create.py"""
    logger.info('  Running the create.py script')

    # Global var
    global headers

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'x-apikeys': f"accessKey={access_key};secretKey={secret_key}"}
    # Var are defined in the scans.ini file
    config = configparser.ConfigParser()
    config.read('scans.ini')
    config_scans_list = config.sections()

    # Declare list for names of scans that will get returned from main()
    # Need this for input to the chains.py script
    scan_name_list = []

    # Lists for handling multiple tag_targets that are comma delimited
    tag_list = []
    tag_list2 = []
    tag_id = ''

    try:
        for section in config_scans_list:
            folder_name = config.get(section, 'folder_name')
            folder_id = folder_dict[folder_name]
            scanner_name = config.get(section, 'scanner_name')
            scanner_id = scanner_dict[scanner_name]
            policy_name = config.get(section, 'policy_name')
            launch = config.get(section, 'launch')
            email = config.get(section, 'email')
            description = config.get(section, 'description')
            scan_name = config.get(section, 'scan_name')
            scan_targets = config.get(section, 'scan_targets')
            # Use regex to grab policy_id and policy_uuID from the
            # policies_dict value string using policy_name as the key
            policy_id = re.sub(':.*', '', policies_dict[policy_name])
            policy_uuid = re.sub('^.*?:', '', policies_dict[policy_name])
            tag_pair = config.get(section, 'tag_target_pair')
            if tag_pair != '':
                # Remove any leading and/or trailing white space around
                # the commas in the comma-delimited tag_pair string. Note
                # that this will not adversely effect tag values that have
                # spaces in them (e.g. Office:San Francisco).
                tag_pair = re.sub('\s{0,},\s{0,}', ',', tag_pair)
                # Similarly, remove any spaces around the colon between them
                # tag name and the tag value (e.g. Office : London)
                tag_pair = re.sub('\s{0,}:\s{0,}', ':', tag_pair)
                tag_list = tag_pair.split(',')
                for pair in tag_list:
                    # Wrap each tag_id with double quotes here in prep for
                    # the API call in the create_scans function
                    tag_id = '"' + tag_dict[pair] + '"'
                    tag_list2.append(tag_id)
                tag_targets = ','.join(tag_list2)
            else:
                tag_targets = ''

            create_scans(policy_uuid, scan_name, description, policy_id,
                         folder_id, scanner_id, launch, scan_targets,
                         email, tag_targets, headers)

            # Add scan name to list
            scan_name_list.append(scan_name)
            # Clear tag_list2 for next scan in scans.ini
            tag_list2 = []

    except:
        error = sys.exc_info()
        logger.info('ERROR: Scan definition in scans.ini is not configured' \
                    ' properly')
        logger.info(f'ERROR: {error}')
        logger.info('Exiting...')
        exit()

    logger.info('Scan creation finished successfully.')
    print ('  See "log.chain" in the logs subdirectory for script output\n')
    return scan_name_list

if __name__ == '__main__':
    print ('\n  Do not execute this script directly.')
    print ('  Instead, execute chain.py using an argument.')
    print ('  Run the command "./chain.py --help" to see usage info.\n')
    print ('  Exiting...\n')
    exit()
