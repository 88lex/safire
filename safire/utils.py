#!/usr/bin/env python3

import os
import sys

sys.path.append("..")
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import pickle
from glob import glob
from pathlib import Path

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config as cf


class Help:
    """These small functions support repeated activities in other classes/functions"""

    def __init__(self):
        super(Help, self).__init__()

    def _svc(self, service, version, tkn):
        try:
            with open(tkn, "rb") as t:
                creds = pickle.load(t)
            return build(service, version, credentials=creds)
        except:
            print("No valid token found")
            auth = Auth()
            auth.check()

    def _export(self, dset, filter, file_tag, fields, ltype, prt=True):
        df = pd.DataFrame(dset)
        fname = f"{ltype}_list_{filter}_{file_tag}"
        pd.set_option("display.max_rows", None)
        df.to_csv("{}/{}.csv".format(cf.data_path, fname))
        df.to_excel("{}/{}.xlsx".format(cf.data_path, fname))
        if prt:
            print(df[fields])
            print(f"  {len(df)} {ltype} found")
            print(
                f"\nData for {ltype} exported to {fname}.csv and .xlsx in folder /{cf.data_path}\n"
            )

    def _print1(self, plist, ltype):
        print("", *plist, sep="\n")
        print(f"  {len(plist)} {ltype} found")

    def _pre_pad(self, prefix, pad, number):
        return prefix + (("0" * pad) + str(number))[-pad:]


class BatchJob:
    def __init__(self, service):
        self.batch = service.new_batch_http_request(callback=self.callback_handler)
        self.batch_resp = []

    def add(self, to_add, request_id=None):
        self.batch.add(to_add, request_id=request_id)

    def callback_handler(self, rid, resp, exception):
        response = {"request_id": rid, "exception": None, "response": None}
        if exception is not None:
            response["exception"] = exception
        else:
            response["response"] = resp
        self.batch_resp.append(response)

    def execute(self):
        try:
            self.batch.execute()
        except:
            pass
        return self.batch_resp


class Auth:
    """Authorize the app to access your projects, SAs, drives and groups. To generate creds.json go to
    https://developers.google.com/apps-script/api/quickstart/python , click Enable then download a json,
    rename it to creds.json and put a copy in the /creds folder"""

    def __init__(self):
        super(Auth, self).__init__()
        self.scopes_proj = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/iam",
        ]
        self.scopes_group = [
            "https://www.googleapis.com/auth/admin.directory.group",
            "https://www.googleapis.com/auth/admin.directory.group.member",
        ]
        self.scopes_all = self.scopes_proj + self.scopes_group

    def ask(self):
        pass

    def check(self):
        filelist = [cf.credentials, cf.token, cf.group_credentials, cf.group_token]
        file_exists = [os.path.isfile(i) for i in filelist]
        [print(f"File = {i[0]} exists = {i[1]}") for i in zip(filelist, file_exists)]
        if not file_exists[0]:
            print(
                f"Credentials file is missing. Download from Google console and run 'auth'"
            )
        if not file_exists[2]:
            print(
                f"Group credentials file is missing. Download from Google console and run 'auth'"
                f"Note that the group credentials file is normally the same as the main projects credentials"
                f"file - But you can optionally use separate credentials files. Specify in config.py"
            )
        yes_no = input("Generate token for projects, SAs, drives? y/n: ")
        if yes_no.lower() in ["y", "yes"]:
            self.projects(cf.credentials, cf.token)
        gyes_no = input("Generate token for groups? y/n: ")
        if gyes_no.lower() in ["y", "yes"]:
            self.groups(cf.group_credentials, cf.group_token)
        exit()

    def projects(self, credentials=cf.credentials, token=cf.token):
        """Create an auth token for accessing and changing projects,
        service accounts, json keys and drives"""
        self.get_token(credentials, self.scopes_proj, token)

    def groups(self, credentials=cf.credentials, group_token=cf.group_token):
        """Create an auth token for adding/removing group members"""
        self.get_token(credentials, self.scopes_group, group_token)

    def all(self, credentials=cf.credentials, token=cf.token):
        """Create an auth token with APIs enabled for projects and groups"""
        self.projects(cf.credentials, cf.token)
        self.groups(cf.group_credentials, cf.group_token)

    def get_token(self, credentials, scopes, token):
        if not credentials or os.path.isfile(credentials[0]):
            print(
                f"Credentials file is missing. Download from Google console and save as {credentials}"
            )
            exit()
        cred_file = glob(credentials)
        creds = None
        if os.path.exists(token):
            with open(token, "rb") as tkn:
                creds = pickle.load(tkn)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_file[0], scopes)
                yes_no = input(
                    "Run local server with browser? If no, generate console link. y/n: "
                )
                if yes_no.lower() in ["y", "yes"]:
                    creds = flow.run_local_server()
                else:
                    creds = flow.run_console()
            with open(token, "wb") as tkn:
                print("Writing/updating token")
                pickle.dump(creds, tkn)
        else:
            print("Credentials and token exist and appear to be valid")
            print(f"credentials = {cred_file[0]} and token = {token}")
            yes_no = input(
                f"Do you want to delete and regenerate your token file = {token}? y/n: "
            )
            if yes_no.lower() in ["y", "yes"]:
                os.remove(token)
                self.get_token(credentials, scopes, token)
            else:
                print("Finished without creating new token")


class Link:
    """Create a symlink between safire's directories and another location"""

    def dirs(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        dest = f"{str(Path.home())}/safire"
        dest1 = input(f"Choose dir to link. To keep default = {dest} press Enter: ")
        if dest1:
            dest = dest1
        if os.path.exists(dest):
            print(f"Directory {dest} already exists. Exiting.")
            exit()
        print(f"Linking {cwd} to {dest}")
        if os.path.isdir(dest):
            os.unlink(dest)
        os.symlink(cwd, dest)
