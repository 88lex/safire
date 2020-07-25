#!/usr/bin/env python3

# import fire
import os
import pickle
# import uuid
from glob import glob

import pandas as pd
# import googleapiclient.discovery
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import *

# from json import loads
# from time import sleep

# from googleapiclient.errors import HttpError
# from googleapiclient import discovery
# from oauth2client.client import OAuth2Credentials as creds


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
        pd.set_option('display.max_rows', None)
        df.to_csv("{}/{}.csv".format(data_path, fname))
        df.to_excel("{}/{}.xlsx".format(data_path, fname))
        if prt:
            print(df[fields])
            print(f"  {len(df)} {ltype} found")
            print(f"\nData for {ltype} exported to {fname}.csv and .xlsx in folder /{data_path}\n")

    def _print1(self, plist, ltype):
        print('', *plist, sep='\n')
        print(f"  {len(plist)} {ltype} found")

    def _pre_pad(self, prefix, pad, number):
        return prefix + (('0' * pad) + str(number))[-pad:]


class BatchJob():

    def __init__(self, service):
        self.batch = service.new_batch_http_request(callback=self.callback_handler)
        self.batch_resp = []

    def add(self, to_add, request_id=None):
        self.batch.add(to_add, request_id=request_id)

    def callback_handler(self, rid, resp, exception):
        response = {'request_id': rid, 'exception': None, 'response': None}
        if exception is not None:
            response['exception'] = exception
        else:
            response['response'] = resp
        self.batch_resp.append(response)

    def execute(self):
        try:
            self.batch.execute()
        except socket.error:
            pass
        return self.batch_resp


class Auth:
    """Authorize the app to access your projects, SAs, drives and groups. To generate creds.json go to
    https://developers.google.com/apps-script/api/quickstart/python , click Enable then download a json,
    rename it to creds.json and put a copy in the /creds folder"""

    def __init__(self):
        super(Auth, self).__init__()
        self.scopes_proj = [
            "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/iam"
        ]
        self.scopes_group = [
            "https://www.googleapis.com/auth/admin.directory.group",
            "https://www.googleapis.com/auth/admin.directory.group.member"
        ]
        self.scopes_all = self.scopes_proj + self.scopes_group

    def ask(self):
        pass

    def check(self):
        filelist = [credentials, token, group_credentials, group_token]
        file_exists = [os.path.isfile(i) for i in filelist]
        [print(f"File = {i[0]} exists = {i[1]}") for i in zip(filelist, file_exists)]
        if not file_exists[0]:
            print(f"Credentials file is missing. Download from Google console and run 'auth'")
            exit()
        if not file_exists[2]:
            print(f"Group credentials file is missing. Download from Google console and run 'auth'")
            exit()
        yes_no = input("Generate token for projects, SAs, drives? y/n: ")
        if yes_no.lower() in ["y", "yes"]:
            self.projects(credentials, token)
        gyes_no = input("Generate token for groups? y/n: ")
        if gyes_no.lower() in ["y", "yes"]:
            self.groups(group_credentials, group_token)
        exit()

    def projects(self, credentials=credentials, token=token):
        """Create an auth token for accessing and changing projects,
        service accounts, json keys and drives"""
        self.get_token(credentials, self.scopes_proj, token)

    def groups(self, credentials=credentials, group_token=group_token):
        """Create an auth token for adding/removing group members"""
        self.get_token(credentials, self.scopes_group, group_token)

    def all(self, credentials=credentials, token=token):
        """Create an auth token for adding/removing group members"""
        self.get_token(credentials, self.scopes_all, token)

    def get_token(self, credentials, scopes, token):
        credentials = glob(credentials)
        creds = None
        if os.path.exists(token):
            with open(token, "rb") as tkn:
                creds = pickle.load(tkn)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials[0], scopes)
                creds = flow.run_local_server()
            with open(token, "wb") as tkn:
                pickle.dump(creds, tkn)
