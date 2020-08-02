# Chain.py - Tenable IO Chained Scanning Application



This application is for querying of the Tenable IO API for customer specific information needed to build a scan configuration file (containing information such as scan policy names and their associated ID number). The scan config file is then used to automate the scan creation, deletion and execution (or "running") of "chained" vulnerability scans, either manually or from a cron job, via the Tenable IO API. Incorporation of the Python ArgParse module to present usage information and flag/argument validation, and the Python ConfigParser module to parse the scans definition file, are supported features as well. Finally, the robust error checking for mis-configured scans in the scan definition file, and use of the Python Logging module to log both to STDOUT and log flat files including log rotation based on max size and count, is supported.

  - Chained vulnerability scanning is defined as: the running, or execution, of a pre-defined set of vulnerability scans, in order, in a sequential manner, where the scan n+1 runs only after scan n has completed.


[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](./CONTRIBUTORS.md)


### Technologies

Chain.py was created with:

* [RedHat Enterprise Linux 7.5](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux)
* [Windows 10](https://www.microsoft.com/en-us/windows/get-windows-10)
* [Python 3.7.4](https://www.activestate.com/products/python/downloads/)
* [Tenable IO](https://www.tenable.com/products/tenable-io)
* [Tenable IO API Explorer](https://developer.tenable.com/reference)
* [Pylint 1.9.5](https://www.pylint.org)

Chain.py was tested and runs on the following platforms using Python 3.7.4: Windows 10 and RHEL Linux 7.5

### Installation

Chain.py requires the following Python modules and libraries to run:

- argparse
- textwrap
- os
- fileconfig
- configparser
- json
- logging
- re
- requests
- sys
- time
- dotenv

NOTE: All but dotenv are in the Python standard library. To install dotenv, run:


```sh
$ pip install python-dotenv
```

### Usage
- Create the .env file in the chain directory of the repo with your IO API keys after you clone the repo or download the release. Stub values are there for replacement. Replace <access_key> and <security_key> with your corresponding user API keys. Then chmod the file 600 (chmod 600 ./.env) if running on Linux. If running on Windows, configure the owernship and permissions of the repo files and directories accordingly. The format of the .env file should be as follows:
```sh
ACCESS_KEY=<access_key>
SECRET_KEY=<secret_key
```
- Run "./chain --action info" and use the information in log.info in the logs subdirectory to update scans.ini. There are examples in the comment block in scans.ini to follow. As many scans can be defined as desired, but there needs to be at least two defined.

- Run chain.py either manually or from cron, or both, as necessary. Use the -h/--help argument for specific usage information as shown below:
```sh
$ ./chain.py --help
usage: chain.py [-h]
                [--action {create,run,delete,create-run,delete-create,delete-create-run,info}]

optional arguments:
  -h, --help            show this help message and exit
  --action {create,run,delete,create-run,delete-create,delete-create-run,info}

                        NOTES:
                        - You cannot delete and then run scans (delete-run), nor create and
                        then delete scans (create-delete). Similarly, create-delete-run is
                        not supported.

                        - The "info" flag will output the folder, scanner, policy, and tag
                        name:ID dictionaries to log.info to assist in building scan
                        definitions in the scans.ini file. Run "./chain.py --action info"
                        to generate this log. The data is also sent to STDOUT, however
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
```

### Screenshots
![picture](images/s10.png)
Figure 1. Execution of chain.py using the command "./chain.py --action create-run" as shown in chain.log  

### Documentation
[See here](documentation/Chaining_Vulnerability_Scans_in_Tenable_IO_Using_Python.md)

### Todo's

 - Test with a password safe such as HashiCorp Vault.
 - Create a unit test suite for use in a CI pipeline.
 - Add an "update" module to update existing scans instead of deleting and recreating them. Recreating scans deletes the scan history from the IO backend. If all you want to do is add an email address to the notifications parameter, an update scan module would be useful.

### License

[MIT](https://github.com/jeff-a-holland/Chain.py---Tenable-IO-Chained-Scanning-Application/blob/master/LICENSE.md)
