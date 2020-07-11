#!/usr/bin/python
"""Create scans in IO using scans.ini config file"""

# Import modules
import json
import sys
import time
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
logger = logging.getLogger('run')

# Local vars
chained_scan_names_in_order_list = []
scan_name_list = []
scan_id_dict = {}
chained_scan_id_list = []
scan_status = ''
previous_scan_history_list = []

# Function to get scan names
def get_scan_names():
    """Get scan names from IO"""
    #Vars are defined in the scans.ini file
    #Parse them for each scan
    config = configparser.ConfigParser()
    config.read('scans.ini')
    config_scans_list = config.sections()

    try:
        for section in config_scans_list:
            scan_name = config.get(section, 'scan_name')
            chained_scan_names_in_order_list.append(scan_name)
    except:
        error = sys.exc_info()[0]
        logger.info('ERROR: Scan definition in scans.ini is not configured' \
                    ' properly')
        logger.info(f'ERROR: {error}')
        logger.info('Exiting...')
        exit()
# End of function

# Function to run scan
def run_scan(scan_id, headers):
    """Run scans defined in scans.ini config file"""
    url = f"https://cloud.tenable.com/scans/{scan_id}/launch"
    response = requests.request("POST", url, headers=headers)
# End function

# Funtion to check scan status
def check_scan_status(scan_id, scan_status, headers):
    """Check status of scan by polling API every 30sec"""
    logger.info('Function check_scan_status has been called')
    while scan_status == 'running' or scan_status == 'pending' or \
          scan_status == 'None':
        url = f"https://cloud.tenable.com/scans/{scan_id}"
        response = requests.request("GET", url, headers=headers)
        pretty_json = json.loads(response.text)
        data3 = (json.dumps(pretty_json, indent=2))
        data_dict3 = json.loads(data3)

        # Don't need a condition for 'None' as scan status is now either
        # pending, running, or completed
        if data_dict3['history'][0].values() and \
           (data_dict3['history'][0]['status'] == 'running' or \
           data_dict3['history'][0]['status'] == 'pending'):
            logger.info(f'Scan ID  {scan_id} still running')
            # Sleep 30sec between successive API calls
            time.sleep(30)
        elif data_dict3['history'][0].values() and \
             data_dict3['history'][0]['status'] == 'completed':
            logger.info(f'Scan completed for scan ID {scan_id}')
            scan_status = 'completed'
    logger.info('Function check_scan_status processing has completed')
# End of function

# main function
def main(access_key, secret_key):
    """Main function for run.py script"""
    logger.info('  Running the run.py script')

    # Global vars
    global history_cntr
    global headers
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'x-apikeys': f"accessKey={access_key};secretKey={secret_key}"}

    # Set history counter for use in preventing clobbering of
    # past instansiation of scans with a new one
    history_cntr = 0
    # Call function to get scan names from scans.ini file
    get_scan_names()
    # Get list of scans
    url = "https://cloud.tenable.com/scans"
    response = requests.request("GET", url, headers=headers)
    pretty_json = json.loads(response.text)
    data = (json.dumps(pretty_json, indent=2))
    data_dict = json.loads(data)
    length = len(data_dict['scans'])
    logger.info(f'Number of total scans in IO instance is: {length}')

    # Beginning of the section that runs scans
    logger.info('Running the following scans in a chained manner,' \
                ' in the following top-down order, one at at time:')

    for scan in chained_scan_names_in_order_list:
        logger.info(f'{scan}')

    # Check if at least two scans are defined in scans.ini as we're doing
    # chained scanning. If not, exit. We can't run scans that don't exist.
    if chained_scan_names_in_order_list == '' or \
       len(chained_scan_names_in_order_list) == 1:
        logger.info('ERROR: At least two scans must be defined in scans.ini')
        logger.info('Exiting...')
        exit()

    cntr = 0
    for scan in data_dict['scans']:
        scan_id = data_dict['scans'][cntr]['id']
        scan_name = data_dict['scans'][cntr]['name']
        cntr += 1
        scan_id_dict[scan_name] = scan_id

    # Counter to see when a scan is defined in scans.ini file
    # but not in IO. This counter should stay 0 if all is well.
    scans_ini_scans_dict_cntr = 0
    #for key, value in scan_id_dict.iteritems():
    for key, value in scan_id_dict.items():
        for scan in chained_scan_names_in_order_list:
            if scan not in scan_id_dict:
                scans_ini_scans_dict_cntr += 1
            if key == scan:
                value = int(value)
                chained_scan_id_list.append(value)

    # Check if we have the same number of scans in scans.ini as in the
    # scans_id_dict dictionary. If not, we're trying to run one or more
    # scans that do not exist in IO. Hence, exit.
    # If not, exit. We can't run scans that don't exist.
    if scans_ini_scans_dict_cntr > 0:
        logger.info('ERROR: One or more scans defined in scans.ini do not' \
                    ' exist in IO')
        logger.info('Exiting...')
        exit()

    list_as_str = str(chained_scan_id_list)
    logger.info('List of scan ID\'s that will run in order, one at at' \
                f' time: {list_as_str}')

    # Populate previous_scan_history_list so we can check later if a second
    # instantiation of the scripts still has any scans running
    for scan_id in chained_scan_id_list:
        url = f"https://cloud.tenable.com/scans/{scan_id}"
        response = requests.request("GET", url, headers=headers)
        pretty_json = json.loads(response.text)
        data2 = (json.dumps(pretty_json, indent=2))
        data_dict2 = json.loads(data2)
        if data_dict2['history'] != []:
            previous_scan_history_list.append( \
            data_dict2['history'][0]['status'])

    # Iterate over the chained_scan_id_list again, this time using
    # the list previous_scan_history_list built above
    for scan_id in chained_scan_id_list:
        url = f"https://cloud.tenable.com/scans/{scan_id}"
        response = requests.request("GET", url, headers=headers)
        pretty_json = json.loads(response.text)
        data4 = (json.dumps(pretty_json, indent=2))
        data_dict4 = json.loads(data4)

        if data_dict4['history'] != []:
            dict_val_as_str = str(data_dict4['history'][0]['status'])
            logger.info(f'History status for scan_id {scan_id} is:' \
                        f'{dict_val_as_str}')

        # Let's check if a previous instantiation of the scripts
        # still has any scans running. If so, exit.
        # This check only gets run when all scans have a 'completed'
        # history status, and it's the first time this if statement
        # is evaluated
        history_list_as_str = str(previous_scan_history_list)
        logger.info('previous_scan_history_list BEFORE historical run' \
                    f' check is: {history_list_as_str}')
        if data_dict4['history'] != [] and \
           data_dict4['history'][0].values() and \
           history_cntr == 0 and \
           ('running' in previous_scan_history_list or \
           'pending' in previous_scan_history_list):
            logger.info(f'Scan for ID {scan_id} is pending, already running ' \
                        'or a second instantiation of this script is' \
                        ' trying to run before the previous one finished')
            history_list_as_str = str(previous_scan_history_list)
            logger.info('previous_scan_history_list AFTER historical' \
                        f' run check is: {history_list_as_str}')
            logger.info(' Exiting....')
            exit()

        if data_dict4['history'] == []:
            #Call function to run scan using scan_id
            run_scan(scan_id, headers)
            logger.info('NOTE: Null scan history')
            logger.info(f'Running scan for ID {scan_id} for the first time')

            # Increment history as no scans in the chain were running
            history_cntr += 1
            # Scan has never run before, so hardcode status.
            # It gets updated in the check_scan_status function.
            scan_status = 'None'
            # Call check_scan_status function, which will wait for a
            # run_status of 'complete' before returning
            check_scan_status(scan_id, scan_status, headers)

        elif data_dict4['history'][0].values() and \
             data_dict4['history'][0]['status'] == 'completed':
            # Call function to run scan using scan_id
            run_scan(scan_id, headers)
            logger.info(f'Scan for ID {scan_id} has run previously and '\
                        'Completed. Will run again now.')

            # Increment history as no scans in the chain were running
            history_cntr += 1
            # Scan has run before, but completed. Run it again and
            # hardcode status to pending.
            # It gets updated in the check_scan_status function.
            scan_status = 'pending'
            # Add scan_id to previous_scan_history_list
            previous_scan_history_list.append(scan_id)
            # Call check_scan_status function, which will wait for a
            # run_status of 'complete' before returning
            check_scan_status(scan_id, scan_status, headers)

        else:
            logger.info('ERROR. Exiting....')
            exit()

    logger.info('Scan execution/running finished successfully.')
    print ('  See "log.chain" in the logs subdirectory for script output\n')

if __name__ == '__main__':
    print ('\n  Do not execute this script directly.')
    print ('  Instead, execute chain.py using an argument.')
    print ('  Run the command "./chain.py --help" to see usage info.\n')
    print ('  Exiting...\n')
    exit()
