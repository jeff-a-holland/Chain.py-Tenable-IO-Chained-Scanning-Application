#!/usr/bin/python
"""Wrapper script for chained vulns scans using IO"""

# Import modules
import argparse
import textwrap
import os
from dotenv import load_dotenv

# Argparse and dotenv documentation:
#   - https://docs.python.org/2/library/argparse.html
#   - https://pypi.org/project/python-dotenv/

# Function to chmod log files 600 (rw for owner only once data has been
# written to the log file.
def fix_perms(filepath):
    """Function for file permission changes"""
    file_status = str(os.path.exists(filepath))
    if file_status == 'True':
        os.chmod(filepath, 0o600)
# End of Function

# Main function
def main():
    """Main function in chain.py"""

    ### Check for existence of .env file in local directory. If not there,
    ### exit.
    file_status = str(os.path.exists('.env'))
    if file_status != 'True':
        print ('\n  The .env file does not exist. Create this file and ' \
               'poplulate it with your API keys per the README.\n')
        print ('Exiting...\n')
        exit()

    ### Load Tenable IO API keys from the .env file stored in the current
    ### directory. Make sure you chmod the file 600 to protect it, and
    ### assign ownership as necessary. A check below will set the perms to
    ### 600 if it's not already. Note this check does not run if using the
    ### -h/--help flag. It only works with create/delete/run args.
    ### Format of the .env is:
    #   ACCESS_KEY=<access key goes here>
    #   SECRET_KEY=<secret key goe shere>
    ###
    load_dotenv()
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')

    ### Check for blank API keys or the stub value in the .env file
    if access_key == '' or secret_key == '' or \
       access_key == '<access_key>' or secret_key == '<secret_key>':
        print ('\n  One or more API keys were not declared in the .env file ' \
               '  properly.')
        print ('  Exiting...\n')
        exit()

    ###Configure command line options using argparse
    parser = argparse.ArgumentParser(formatter_class=\
                                     argparse.RawTextHelpFormatter)
    parser.add_argument('--action', choices=['create', 'run', 'delete',
                                             'create-run', 'delete-create',
                                             'delete-create-run', 'info'],
                        help=textwrap.dedent('''
NOTES:
- You cannot delete and then run scans (delete-run), nor create and
then delete scans (create-delete). Similarly, create-delete-run is
not supported.

- The "info" flag will output the folder, scanner, policy, and tag
name:ID dictionaries to log.info to assist in buildiling scan
definitions in the scans.ini file. Run "./chain.py --action info"
to geneate this log. The data is also sent to STDOUT, however
it is easier to search/grep from the log.info flat file.

- The create/delete/run scripts all log to log.chain in the logs
subdirectory. The log file is set to rotate when the size reaches
100K bytes, and keeps a history of 5 log files (log.chain.5 being
the oldest and log.chain being the current). Successive
instantiations of the run.py script will also log to log.chain.
The script name is in the log.chain file, such as "create.py" in
the second field (fields delimited by double-colons). Note that
the log.info file is cleared on every run of the
create/delete/run scripts. This is fine as this data is mutable
and should be queried every time a scan in scans.ini is configured
or updated.

'''))

    args = parser.parse_args()

    # Test to see if logs subdir exists, and if not, create/chmod it
    if not os.path.exists('logs'):
        os.makedirs('logs')
        os.chmod('logs', 0o700)

    # Test if .env file exists, and if so, chmod it. This file contains
    # your API keys, so needs to be secured as much as file permissions
    # allow. Note this check is not executed when using the -h/--help
    # argument. These perms should alrady be 600, but double checking.
    fix_perms('./.env')

    # Check for --action arguments. Will import
    # necessary .py scripts to create .pyc bytecode
    # files. Also run fix_perms function to chmod file.
    if args.action == 'create':
        import info
        info.main(access_key, secret_key)
        import create
        create.main(access_key, secret_key, info.folder_dict, \
                    info.scanner_dict, info.policies_dict, info.tag_dict)
        fix_perms('./logs/log.chain')

    elif args.action == 'run':
        import run
        run.main(access_key, secret_key)
        fix_perms('./logs/log.chain')

    elif args.action == 'delete':
        import delete
        delete.main(access_key, secret_key)
        fix_perms('./logs/log.chain')

    elif args.action == 'create-run':
        import info
        info.main(access_key, secret_key)
        import create
        create.main(access_key, secret_key, info.folder_dict, \
                    info.scanner_dict, info.policies_dict, info.tag_dict)
        import run
        run.main(access_key, secret_key)
        fix_perms('./logs/log.chain')

    elif args.action == 'delete-create':
        import delete
        delete.main(access_key, secret_key)
        import info
        info.main(access_key, secret_key)
        import create
        create.main(access_key, secret_key, info.folder_dict, \
                    info.scanner_dict, info.policies_dict, info.tag_dict)
        fix_perms('./logs/log.chain')

    elif args.action == 'delete-create-run':
        import delete
        delete.main(access_key, secret_key)
        import info
        info.main(access_key, secret_key)
        import create
        create.main(access_key, secret_key, info.folder_dict, \
                    info.scanner_dict, info.policies_dict, info.tag_dict)
        import run
        run.main(access_key, secret_key)
        fix_perms('./logs/log.chain')

    elif args.action == 'info':
        import info
        info.main(access_key, secret_key)
        fix_perms('./logs/log.info')

    else:
        print ('\n  ERROR. No arguments supplied when runing the chain.py script.')
        print ('  Run "./chain.py --help" to see usage info.\n')
        print ('  Exiting...\n')
        exit()

if __name__ == '__main__':
    main()
