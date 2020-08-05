#!/usr/bin/env python3
import os
from pathlib import Path

### These config variables can be customized for each user as needed        ###
###############################################################################
num_new_projects = 1
max_projects = 100
next_project_num = 1
next_sa_num = 1
sas_per_project = 100
next_json_num = 1

###   Prefixes for SA email (required), the project (required) and the downloaded json key (optional)
email_prefix = "svcacc"
# Project prefix must be unique across all of Google, not just your account.
project_prefix = ""
# Leave json_prefix as "" if no json key prefix needed
json_prefix = ""
# You can specify a group address here or as a flag in the relevant commands
group_address = ""

### Config variables below are normally not changed by the user             ###
###############################################################################

# 'dir' = default home dir. Can change to any e.g. = "/somedir/safire"
# dir = '/opt/safire'
dir = f"{str(Path.home())}/safire"

# These dirs and files are located below the path set as 'dir ='
sa_path = f"{dir}/svcaccts"
data_path = f"{dir}/data"
cred_path = f"{dir}/creds"
credentials = f"{cred_path}/creds.json"
token = f"{cred_path}/token.pickle"

# Group token and credentials can be in a different domain than SAs
# If group is in the same account as your projects/drives then copy from above
group_credentials = f"{cred_path}/creds.json"
group_token = f"{cred_path}/grptoken.pickle"
sleep_time = 10
retry = 10
nPT = "nextPageToken"

# 'pad' vars set zero padding for names. e.g. jpad=6 yields 000001.json. Set to 1 if no prefix needed.
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

### Generate empty directories for key files if they do not exist
if not os.path.isdir(dir):
    os.mkdir(dir)
if not os.path.isdir(sa_path):
    os.mkdir(sa_path)
if not os.path.isdir(cred_path):
    os.mkdir(cred_path)
if not os.path.isdir(data_path):
    os.mkdir(data_path)
