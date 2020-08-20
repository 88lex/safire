#!/usr/bin/env python3

import os
import sys

# sys.path.insert(0, os.path.abspath("../"))
sys.path.append("..")
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import fire
import uuid
from base64 import b64decode
from glob import glob
from json import loads
from pathlib import Path
from shutil import copyfile
from time import sleep

# base_path = "/opt"
base_path = str(Path.home())
saf_dir = os.path.join(base_path, "safire")
os.makedirs(saf_dir, exist_ok=True)

cfg_file = os.path.join(saf_dir, "config.py")
loc_cfg_file = os.path.join(os.getcwd(), "config.py")
if os.path.exists(cfg_file):
    copyfile(cfg_file, loc_cfg_file)
else:
    copyfile("default_config.py", loc_cfg_file)
    copyfile("default_config.py", cfg_file)

import config as cf
import utils as ut


class Commands:
    """safire creates projects, service accounts(SAs), json keys for SAs and adds SAs as group members.\n Type -h
    or --help after any command for info.  Usage: './safire list projects' or 'safire add members mygroup@domain.com'
    Most commands accept a 'filter'to process subsets. If no filter all items are listed."""

    def __init__(self):
        # Init()
        self.list = List()
        self.add = Add()
        self.remove = Remove()
        self.auth = ut.Auth()
        self.rename = Rename()
        self.link = ut.Link()
        # alias commands for ease of use. e.g. 'safire add projects' = 'safire create projects'
        self.create = self.add
        self.enable = self.add
        self.delete = self.remove


class List(ut.Help):
    """List drives, projects, service accounts (SAs), SA json keys, groups and group members. 
    In most cases a filter can be applied."""

    def __init__(self):
        super(List, self).__init__()

    def drives(self, filter="", file_tag="", token=cf.token, prt=True):
        """List team/shared drives. Match 'filter'"""
        drivelist = []
        resp = {f"{cf.nPT}": None}
        drive = self._svc(*cf.DRIVE, token)
        while cf.nPT in resp:
            resp = (
                drive.drives()
                .list(
                    fields=f"{cf.nPT}, drives(id,name)",
                    pageSize=100,
                    pageToken=resp[f"{cf.nPT}"],
                )
                .execute()
            )
            drivelist += resp["drives"]
        drivelist = [i for i in drivelist if str(filter) in i["name"]]
        if not prt:
            return drivelist
        self._export(drivelist, filter, file_tag, ["id", "name"], "drives", prt)

    def projects(self, filter="", file_tag="", token=cf.token, prt=True, exact=False):
        """List projects. Match 'filter'"""
        cloud = self._svc(*cf.CLOUD, token)
        plist = cloud.projects().list().execute()["projects"]
        plist = [i for i in plist if str(filter) in i["projectId"]]
        if exact:
            plist = [i for i in plist if str(filter) == i["projectId"]]
        if not prt:
            return [i["projectId"] for i in plist]
        self._export(
            plist,
            filter,
            file_tag,
            ["projectNumber", "projectId", "name"],
            "projects",
            prt,
        )

    def sas(self, filter="", exact=False, file_tag="", token=cf.token, prt=True):
        """List service accounts for projects. Projects match 'filter'.
        Use '--exact=True' flag for exact project match."""
        svcacctlist, sa_summary = [], []
        projId_list = self.projects(filter, file_tag, token, False, exact)
        # if exact:
        #     projId_list = [i for i in projId_list if i == filter]
        iam = self._svc(*cf.IAM, token)
        for project in sorted(projId_list):
            try:
                resp = (
                    iam.projects()
                    .serviceAccounts()
                    .list(name="projects/" + project, pageSize=100)
                    .execute()
                )["accounts"]
                svcacctlist += resp
                sa_summary += [
                    f"  {len(resp)} service accounts (SAs) found in project: {project}"
                ]
            except:
                sa_summary += [
                    f"  No service accounts (SAs) found in project: {project}"
                ]
                continue
        svcacctlist.sort(key=lambda x: x.get("email"))
        if not prt:
            return (
                [i["email"] for i in svcacctlist],
                [i["uniqueId"] for i in svcacctlist],
            )
        if svcacctlist:
            self._export(svcacctlist, filter, file_tag, ["email"], "svc_accts")
        print("\nSummary:", *sa_summary, sep="\n")

    def groups(self, filter="", file_tag="", group_token=cf.group_token, prt=True):
        """List groups in the authorized account. Match 'filter'"""
        svc = self._svc(*cf.ADMIN, group_token)
        grouplist = svc.groups().list(customer="my_customer").execute()["groups"]
        grouplist = [i for i in grouplist if str(filter) in i["email"]]
        if not prt:
            return [i["email"] for i in grouplist]
        self._export(
            grouplist,
            filter,
            file_tag,
            ["id", "email", "directMembersCount"],
            "groups",
            prt,
        )

    def members(self, filter="", file_tag="", group_token=cf.group_token, prt=True):
        """List members in groups. Groups match 'filter'"""
        memberslist, member_summary = [], []
        group_list = self.groups(filter, file_tag, group_token, False)
        svc = self._svc(*cf.ADMIN, group_token)
        for group in group_list:
            try:
                response = []
                resp = {"nextPageToken": None}
                while "nextPageToken" in resp:
                    resp = (
                        svc.members()
                        .list(groupKey=group, pageToken=resp["nextPageToken"])
                        .execute()
                    )
                    response += resp["members"]
                memberslist += response
            except:
                member_summary += [f"  No members found in group: {group}"]
                continue
            member_summary += [f"  {len(response)} members found in group: {group}"]
        if not prt:
            return sorted([i["email"] for i in memberslist if i["role"] != "OWNER"])
        self._export(memberslist, filter, file_tag, ["email", "role"], "members")
        print("\nSummary:", *member_summary, sep="\n")

    def jsons(self, sa_path=cf.sa_path, filter="", file_tag="", prt=True):
        """alias: jsons = keys. List service account jsons/keys in the svcaccts folder. Match 'filter'"""
        keys = glob("%s/*.json" % sa_path)
        json_keys = []
        [json_keys.append(loads(open(key, "r").read())) for key in keys]
        if filter:
            json_keys = [key for key in json_keys if str(filter) in key["project_id"]]
        if prt and json_keys:
            self._export(
                json_keys, filter, file_tag, ["client_email"], "json_keys", prt
            )
            print(f"There are {len(json_keys)} json keys in {sa_path}")
        elif json_keys:
            return [i["client_email"] for i in json_keys]
        else:
            print(f"No json keys in path: {sa_path} matching filter: {filter}")

    keys = jsons

    def all(self):
        """List all drives, projects, service accounts, json keys, groups and group members.
        Also exports these lists with full data fields to csv and xlsx files in data_path folder"""
        self.drives()
        self.projects()
        self.sas()
        self.groups()
        self.members()
        self.jsons()

    def count(self):
        """Count drives, projects, service accounts, json keys, groups and group members."""
        list_drives = []
        list_drives = self.drives("", "", cf.token, False)
        print("Drive count  :", len(list_drives))
        list_projects = []
        list_projects = self.projects("", "", cf.token, False)
        print("Project count:", len(list_projects))
        list_groups = []
        list_groups = self.groups("", "", cf.group_token, False)
        print("Group count  :", len(list_groups))
        try:
            list_jsons = self.jsons(cf.sa_path, "", "", False)
            print("JSON count   :", len(list_jsons))
        except:
            print("JSON count   : 0")
        list_sas = []
        list_sas, _ = self.sas("", False, "", cf.token, False)
        print("SA count     :", len(list_sas))
        list_members = []
        list_members = self.members("", "", cf.group_token, False)
        print("Member count :", len(list_members))


class Add(ut.Help):
    """Add projects, drives, service accounts(SAs), SA keys/jsons and group members"""

    def __init__(self):
        super(Add, self).__init__()
        self._list = List()

    def projects(
        self,
        num_new_projects=cf.num_new_projects,
        next_project_num=cf.next_project_num,
        project_prefix=cf.project_prefix,
        retry=5,
        token=cf.token,
        ppad=4,
        prt=False,
    ):
        """Create projects in authorized account. Usage: 'safire add projects 1'.
        Uses defaults in config if none specified."""
        cloud = self._svc(*cf.CLOUD, token)
        batch = ut.BatchJob(cloud)
        start_projs = self._list.projects("", "", token, prt)
        start_proj_count = len(start_projs)
        num_proj_created = 0
        curr_projects = []
        proj_count = 0
        print(f"Creating {num_new_projects} new projects")
        retries = retry
        while num_new_projects and retries:
            new_projs = [
                self._pre_pad(project_prefix, ppad, next_project_num + i)
                for i in range(num_new_projects)
            ]
            for proj in new_projs:
                batch.add(
                    cloud.projects().create(body={"project_id": proj, "name": proj})
                )
            batch.execute()
            retries -= 1
            curr_projects = self._list.projects("", "", token, prt)
            proj_count = len(curr_projects)
            num_proj_created = proj_count - start_proj_count
            next_project_num = next_project_num + num_proj_created
            num_new_projects = num_new_projects - num_proj_created
        if num_proj_created < 1:
            print(
                "0 projects created. Your project prefix + number may be used already",
                "somewhere else in Google. Try changing your prefix.",
            )
            exit()
        new_projs = [i for i in curr_projects if i not in start_projs]
        print(f"\nCreated {num_proj_created} projects:", *new_projs, sep="\n")
        print(f"Total project count = {proj_count}")
        print(
            "Sleep briefly to allow backend to register projects. Then enabling services.\n"
        )
        sleep(cf.sleep_time)
        for proj in new_projs:
            self.apis(proj)

    def apis(
        self, filter="", svcs_to_enable=cf.svcs_to_enable, token=cf.token, prt=False
    ):
        """Enables apis for projects. 'drive' and 'iam' apis by default. Automatic when projects are
        created but can be run manually also."""
        svcusage = self._svc(*cf.SVCUSAGE, token)
        projId_list = self._list.projects(filter, "", token, prt)
        batch = ut.BatchJob(svcusage)
        svcs_to_enable = [i + ".googleapis.com" for i in svcs_to_enable]
        for project in projId_list:
            for svc1 in svcs_to_enable:
                print(f"Enabling service: {svc1} in project: {project}")
                batch.add(
                    svcusage.services().enable(
                        name=f"projects/{project}/services/{svc1}"
                    )
                )
            batch.execute()

    def sas(
        self,
        filter="",
        sas_per_project=cf.sas_per_project,
        email_prefix=cf.email_prefix,
        next_sa_num=cf.next_sa_num,
        retry=cf.retry,
        exact=False,
        file_tag="",
        prt=False,
    ):
        """Create N service accounts/SAs in projects which match 'filter'. Usage: 'safire add sas xyz 5'
         will add 5 SAs to all projects containing 'xyz' if fewer than 100 exist. Will not overwrite SAs."""
        iam = self._svc(*cf.IAM, cf.token)
        projId_list = self._list.projects(filter, file_tag, cf.token, prt)
        all_sas = []
        for project in projId_list:
            # batch = ut.BatchJob(iam)
            sa_emails, _ = self._list.sas(project, True, file_tag, cf.token, False)
            start_sa_emails = sa_emails
            start_sa_count = len(sa_emails)
            all_sas = all_sas + sa_emails
            count = min(sas_per_project, 100 - len(sa_emails))
            print(
                len(sa_emails), "SAs exist. Creating", count, "SAs in project", project
            )
            new_sas = []
            retries = retry
            while count and retries:
                batch = ut.BatchJob(iam)
                for _ in range(count):
                    while [s for s in all_sas if str(next_sa_num) in s.split("@")[0]]:
                        next_sa_num += 1
                    sa_id = self._pre_pad(email_prefix, cf.spad, next_sa_num)
                    new_sas.append(sa_id)
                    next_sa_num += 1
                    name = f"projects/{project}"
                    body = {
                        "accountId": sa_id,
                        "serviceAccount": {"displayName": sa_id},
                    }
                    batch.add(
                        iam.projects().serviceAccounts().create(name=name, body=body)
                    )
                batch.execute()
                retries -= 1
                sa_emails, _ = self._list.sas(project, True, file_tag, cf.token, False)
                curr_sa_count = len(sa_emails)
                count = count - curr_sa_count + start_sa_count
                sleep(cf.sleep_time / 4)
            new_sa_emails = [i for i in sa_emails if i not in start_sa_emails]
            num_sas_created = len(new_sa_emails)
            print(
                f"\nCreated {num_sas_created} sas in {project}:",
                *new_sa_emails,
                sep="\n",
            )
            print(f"Total SAs in {project} count = {len(sa_emails)}")

    def jsons(
        self,
        filter="",
        sa_path=cf.sa_path,
        next_json_num=cf.next_json_num,
        json_prefix=cf.json_prefix,
        jpad=cf.jpad,
        retry=cf.retry,
        file_tag="",
        token=cf.token,
        prt=False,
    ):
        """Create and download json/key files to svcaccts folder. Add to TDs and/or groups."""
        iam = self._svc(*cf.IAM, token)
        projId_list = self._list.projects(filter, file_tag, token, prt)
        for project in sorted(projId_list):
            batch = ut.BatchJob(iam)
            _, sa_uniqueId = self._list.sas(project, True, file_tag, token, prt)
            num_sas = len(sa_uniqueId)
            print(f"Downloading {str(len(sa_uniqueId))} SA keys in project {project}")
            resp = []
            retries = retry
            while len(resp) < num_sas and retries:
                for sa in sa_uniqueId:
                    batch.add(
                        iam.projects()
                        .serviceAccounts()
                        .keys()
                        .create(
                            name=f"projects/{project}/serviceAccounts/{sa}",
                            body={
                                "privateKeyType": "TYPE_GOOGLE_CREDENTIALS_FILE",
                                "keyAlgorithm": "KEY_ALG_RSA_2048",
                            },
                        )
                    )
                resp = [i["response"] for i in batch.execute()]
                retries -= 1
            for i in resp:
                if i is not None:
                    k = (
                        i["name"][i["name"].rfind("/") :],
                        b64decode(i["privateKeyData"]).decode("utf-8"),
                    )[1]
                    json_name = self._pre_pad(json_prefix, jpad, next_json_num)
                    with open("%s/%s.json" % (sa_path, json_name), "w+") as f:
                        f.write(k)
                    next_json_num += 1
            sleep(cf.sleep_time)

    keys = jsons

    def drive(self, td_name):
        """Create a team/shared drive. Usage: 'safire add drive some_name'"""
        drive = self._svc(*cf.DRIVE, cf.token)
        body = {"name": td_name}
        driveId = (
            drive.drives()
            .create(body=body, requestId=str(uuid.uuid4()), fields="id,name")
            .execute()
            .get("id")
        )
        print(f"  Drive ID for {td_name} is {driveId}")
        return td_name, driveId

    def drives(self, *td_list):
        """Create team/shared drives. Usage: 'safire add drives some_filename' containing 
        a list of drive names OR `safire add drives mytd1 mytd2 mytd3`"""
        td_file = " ".join(sys.argv[3:]).strip('"')
        if os.path.isfile(td_file):
            with open(td_file, "r") as td_lst:
                td_list = [i for i in td_lst]
        for td_name in td_list:
            print(f"Creating {td_name}")
            self.drive(td_name.rstrip())

    def members(
        self,
        project_filter,
        group_filter,
        retry=5,
        file_tag="",
        group_token=cf.group_token,
        prt=False,
    ):
        """'add members' requires two arguments. Both 'project_filter' and 'group_filter' can be either the full
        project/group name or a partial name which matches some projects/groups. 
        You can add SA emails from multiple projects to multiple groups if you wish."""
        admin = self._svc(*cf.ADMIN, group_token)
        projId_list = self._list.projects(project_filter, file_tag, cf.token, prt)
        group_list = self._list.groups(group_filter, file_tag, group_token, prt)
        for group in group_list:
            for project in projId_list:
                batch = ut.BatchJob(admin)
                sa_emails, _ = self._list.sas(project, True, file_tag, cf.token, False)
                if len(sa_emails) == 0:
                    print("No service accounts found in", project)
                    continue
                group_members = self._list.members(group, file_tag, group_token, prt)
                add_sas = [i for i in sa_emails if i not in group_members]
                if len(add_sas) == 0:
                    continue
                print(
                    f"Adding {str(len(add_sas))} SAs to group: {group} from project: {project}"
                )
                retries = retry
                while add_sas and retries:
                    retries -= 1
                    for email in add_sas:
                        batch.add(
                            admin.members().insert(
                                groupKey=group, body={"email": email, "role": "MEMBER"}
                            )
                        )
                    batch.execute()
                    sleep(cf.sleep_time)
                    group_members = self._list.members(
                        group_filter, file_tag, group_token, prt
                    )
                    add_sas = [i for i in sa_emails if i not in group_members]
                print(
                    f"{len(sa_emails)-len(add_sas)} SA emails from {project} are in {group}. {len(add_sas)} failed."
                )

    def user(self, user, *td_id, role="organizer"):
        """Add user (typically group name) to shared/team drive(s). Usage: 'safire add mygroup@domain.com td_filter'"""
        for td_filt in td_id:
            drives = self._list.drives(td_filt, "", token, False)
            for td in drives:
                if td_filt in td["name"]:
                    print(f"Adding {user} to {td['name']} {td['id']}")
                    drive = self._svc(*cf.DRIVE, cf.token)
                    body = {"type": "user", "role": role, "emailAddress": user}
                    drive.permissions().create(
                        body=body, fileId=td["id"], supportsAllDrives=True, fields="id"
                    ).execute()
                else:
                    pass


class Remove(ut.Help):
    """Delete sas, jsons/keys, drives and group members. Note: 'remove' and 'delete' are equivalent commands"""

    def __init__(self):
        super(Remove, self).__init__()
        self._list = List()

    def sas(
        self,
        project_filter,
        token=cf.token,
        exact=False,
        file_tag="",
        prt=False,
        retry=cf.retry,
    ):
        """Usage: 'safire remove sas filter' where filter is a string to match the projects from which 
        you want to delete service accounts. To remove all SAs for all projects use "" as your filter"""
        projId_list = self._list.projects(project_filter, file_tag, token, prt)
        iam = self._svc(*cf.IAM, token)
        for project in projId_list:
            sas, _ = self._list.sas(project, True, file_tag, token, False)
            retries = retry
            while sas and retries:
                retries -= 1
                if len(sas) == 0:
                    print(f"0 service accounts in {project}. Moving to next project")
                    continue
                batch = ut.BatchJob(iam)
                print(f"Removing {len(sas)} service accounts from {project}")
                for i in sas:
                    name = f"projects/{project}/serviceAccounts/{i}"
                    batch.add(iam.projects().serviceAccounts().delete(name=name))
                batch.execute()
                sas, _ = self._list.sas(project, True, file_tag, token, False)

    def jsons(self, filter="", sa_path=cf.sa_path):
        """Remove json keys from svcaccts path"""
        _, _, files = next(os.walk(sa_path))
        if not files:
            return f"No json keys found in {sa_path}, Nothing to delete"
        delete_files = [i for i in sorted(files) if ".json" and str(filter) in i]
        print(f"Files to be deleted:\n", *delete_files, sep="\n")
        yes_no = input("Confirm you want to delete all of these files. y/n: ")
        if yes_no.lower() in ["y", "yes"]:
            for file in delete_files:
                print(f"Removing {file}")
                os.remove(f"{sa_path}/{file}")
        else:
            print("Deletion of json files aborted")

    def members(
        self,
        group_filter,
        retry=cf.retry,
        batch_size=100,
        file_tag="",
        group_token=cf.group_token,
        prt=False,
    ):
        """Remove members from groups. Match 'filter'"""
        admin = self._svc(*cf.ADMIN, group_token)
        batch = ut.BatchJob(admin)
        group_list = self._list.groups(group_filter, file_tag, group_token, prt)
        group_members = []
        for group in group_list:
            group_members = self._list.members(group, file_tag, group_token, prt)
            retries = retry
            while len(group_members) > 1 and retries:
                print(
                    f"Removing {str(len(group_members))} SAs from group: {group}. Batch = {batch_size}"
                )
                retries -= 1
                for member in group_members[:batch_size]:
                    batch.add(admin.members().delete(groupKey=group, memberKey=member))
                batch.execute()
                batch = ut.BatchJob(admin)
                group_members = self._list.members(group, file_tag, group_token, prt)
            print(
                f"{len(group_members)} members remaining in {group} (excluding OWNER)"
            )

    def drive(self, teamDriveId, token=cf.token):
        """Delete a team/shared drive. Usage: 'safire add teamdrive unique ID'. USE CAREFULLY!
        Does not work with non-empty drives."""
        drvsvc = self._svc(*cf.DRIVE, token)
        drives = self._list.drives(teamDriveId, "", token, False)
        print("Drives to be removed:", *drives, sep="\n")
        yes_no = input("Confirm you want to delete all of these drives. y/n: ")
        if not yes_no.lower() in ["y", "yes"]:
            return "Deletion of drives aborted"
        for drive in drives:
            print(f"Removing drive: {drive['name']} with id: {drive['id']}")
            drvsvc.drives().delete(driveId=str(drive["id"])).execute()

    def drives(self, input_file, token=cf.token):
        """Delete team/shared drives. Usage: 'safire add teamdrive some_filename' with unique IDs. USE CAREFULLY"""
        td_list = open(input_file, "r")
        for teamDriveId in td_list:
            print(f"Deleting {teamDriveId}")
            self.drive(teamDriveId.rstrip())

    def user(self, user, *td_id, role="organizer", token=cf.token):
        """Remove user (typically group name) from shared/team drive(s). Usage: 'safire remove mygroup@domain.com td_filter'"""
        drives = self._list.drives("", "", token, False)
        for td_filt in td_id:
            for td in drives:
                if td_filt in td["name"]:
                    drvsvc = self._svc(*cf.DRIVE, token)
                    user_info = []
                    resp = {"nextPageToken": None}
                    while "nextPageToken" in resp:
                        resp = (
                            drvsvc.permissions()
                            .list(
                                fileId=td["id"],
                                pageSize=100,
                                fields="nextPageToken,permissions(id,emailAddress,role)",
                                supportsAllDrives=True,
                                pageToken=resp["nextPageToken"],
                            )
                            .execute()
                        )
                        user_info += resp["permissions"]
                    for i in user_info:
                        if user in i["emailAddress"]:
                            print(
                                f"Removing {user} with id {i['id']} from {td['name']} {td['id']}"
                            )
                            drvsvc.permissions().delete(
                                permissionId=i["id"],
                                fileId=td["id"],
                                supportsAllDrives=True,
                                fields="id",
                            ).execute()


class Rename:
    """Rename json/key files to their email prefix, email numeric (omit prefix), uniqId or in a sequence.
    Usage: 'safire rename jsons email'  [choice email, email_seq, uniq, seq]
    Renaming is repeatable. Can always delete and redownload keys if needed."""

    def jsons(self, rename_type, dir=f"{cf.sa_path}/"):
        """Usage: 'safire rename jsons email'  [choice email, email_seq, uniq, seq]"""
        import json, os

        filelist = os.listdir(dir)
        print("\nOriginal filenames:", *sorted(filelist), sep="\n")
        new_name = []
        if rename_type == "seq":
            [
                os.rename(dir + file, dir + f"{i+1}.json")
                for i, file in enumerate(sorted(filelist))
            ]
        else:
            for file in sorted(filelist):
                try:
                    with open(dir + file) as f:
                        data = json.load(f)
                        if rename_type == "email":
                            new_name = data["client_email"].split("@")[0] + ".json"
                        if rename_type == "email_seq":
                            digits = list(
                                filter(
                                    lambda x: x.isdigit(),
                                    data["client_email"].split("@")[0],
                                )
                            )
                            new_name = "".join(digits) + ".json"
                        if rename_type == "uniq":
                            new_name = data["client_id"] + ".json"
                        if os.path.exists(dir + new_name):
                            continue
                        os.rename(dir + file, dir + new_name)
                except:
                    continue
        print("\nCurrent filenames:", *sorted(os.listdir(dir)), sep="\n")


def main():
    fire.Fire(Commands)


if __name__ == "__main__":
    main()
