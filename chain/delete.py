#!/usr/bin/python
"""Deletes scans from IO using scans.ini config file"""

# Import modules
import json
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
logger = logging.getLogger('delete')

# Local vars
scan_name_list = []
scan_id_dict = {}

# Function to get scan names
def get_scan_names(headers):
    """Get scan names from scans.ini"""
    # Var are defined in the scans.ini file
    config = configparser.ConfigParser()
    config.read('scans.ini')
    config_scans_list = config.sections()

    try:
        for section in config_scans_list:
            scan_name = config.get(section, 'scan_name')
            scan_name_list.append(scan_name)
    except:
        error = sys.exc_info()
        logger.info('ERROR: Scan definition in scans.ini is not configured' \
        ' properly')
        logger.info(f'ERROR: {error}')
        logger.info('Exiting...')
        exit()
# End of function

# Function to get scan id's
def get_scan_ids(headers):
    """Get scanner ID's from IO"""
    url = "https://cloud.tenable.com/scans"
    response = requests.request("GET", url, headers=headers)
    pretty_json = json.loads(response.text)
    data = (json.dumps(pretty_json, indent=2))
    data_dict = json.loads(data)

    cntr = 0
    for scan in data_dict['scans']:
        scan_id = data_dict['scans'][cntr]['id']
        scan_name = data_dict['scans'][cntr]['name']
        cntr += 1
        scan_id_dict[scan_name] = scan_id
# End of function

# Function to delete scans
def delete_scans(headers):
    """Delete scans in IO using scan names in scans.ini"""
    for scan_name in scan_name_list:
        if scan_name in scan_id_dict:
            scan_id = scan_id_dict[scan_name]
            scan_name = '"'.join([scan_name])
            url = f"https://cloud.tenable.com/scans/{scan_id}"
            response = requests.request("DELETE", url, headers=headers)
            logger.info(f'Deleting scan "{scan_name}" with scan_id {scan_id}')
        else:
            logger.info('This scan does not exist in IO. Skipping ' \
                        f'DELETE API call for: "{scan_name}"')
# End of function

# main function
def main(access_key, secret_key):
    """Main function for delete.py"""
    logger.info('  Running the delete.py script')

    # Global var
    global headers

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'x-apikeys': f"accessKey={access_key};secretKey={secret_key}"}
    get_scan_names(headers)
    get_scan_ids(headers)
    delete_scans(headers)
    logger.info('Scan deletion finished successfully.')
    print ('\n  See "log.chain" in the logs subdirectory for script output\n')

if __name__ == '__main__':
    print ('\n  Do not execute this script directly.')
    print ('  Instead, execute chain.py using an argument.')
    print ('  Run the command "./chain.py --help" to see usage info.\n')
    print ('  Exiting...\n')
    exit()
