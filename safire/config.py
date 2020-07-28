#!/usr/bin/env python3

########################################################################
### These config variables can be customized for each user as needed ###
num_new_projects = 1
max_projects = 100
next_project_num = 1
next_sa_num = 1
sas_per_project = 100
next_json_num = 1

###   Prefixes for SA email (required), the project (required) and the downloaded json key (optional)
email_prefix = "svcacc"
# Project prefix must be unique across all of Google, not just your account.
project_prefix = "syncqwerty"
# Leave json_prefix as "" if no json key prefix needed
json_prefix = ""

########################################################################
### Config variables below are normally not changed by the user      ###
# files_path = "/opt/safire/safire"
files_path = "/opt/data"
sa_path = "svcaccts"
credentials = "creds/creds.json"
token = "creds/token.pickle"
data_path = "data"

### Group token and credentials can be in a different domain than SAs            ###
### If group is in the same account as your projects/drives then copy from above ###
group_credentials = "creds/creds.json"
group_token = "creds/grptoken.pickle"
group_address = "mygroup@domain.com"
sleep_time = 5
retry = 5
nPT = "nextPageToken"

### ['pad' vars set zero padding for names. e.g. jpad=6 yields 000001.json. Set to 1 if not prefix needed.] ###
ppad = 4
spad = 6
jpad = 6

### [API Service Names and Versions]
DRIVE = ["drive", "v3"]
CLOUD = ["cloudresourcemanager", "v1"]
IAM = ["iam", "v1"]
ADMIN = ["admin", "directory_v1"]
SVCUSAGE = ["serviceusage", "v1"]
svcs_to_enable = ["iam", "drive"]

### Add path to creds, service accounts and csv/xlsx files
sa_path = f"{files_path}/{sa_path}"
credentials = f"{files_path}/{credentials}"
token = f"{files_path}/{token}"
data_path = f"{files_path}/{data_path}"
group_credentials = f"{files_path}/{group_credentials}"
group_token = f"{files_path}/{group_token}"
