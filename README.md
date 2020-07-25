# SAFIRE
## A flexible tool to create and delete service accounts to be used with shared drives.

- Simple usage syntax: e.g. `safire list projects`
- Available main commands:
    - list
    - add / create
    - remove / delete
    - auth
    - enable
    - rename

- Most commands will tell you which subcommands are available by simply typing the main command with no flags. e.g. `safire list` or optionally `safire list -h` . Subcommands include:
    - projects
    - sas - aka service accounts
    - keys / jsons
    - groups
    - members


## Detailed commands

__list__

    `safire list`

SYNOPSIS

    `safire list COMMAND`

DESCRIPTION

    List drives, projects, service accounts (SAs), SA json keys, groups and group members. In most cases a filter can be applied.

COMMANDS

    COMMAND is one of the following:

     all
       List all drives, projects, service accounts, json keys, groups and group members. Also exports these lists with full data fields to csv and xlsx files in data_path folder

     drives
       List team/shared drives. Match 'filter'

     groups
       List groups in the authorized account. Match 'filter'

     jsons
       alias: jsons = keys. List service account jsons/keys in the svcaccts folder. Match 'filter'

     keys
       alias: jsons = keys. List service account jsons/keys in the svcaccts folder. Match 'filter'

     members
       List members in groups. Groups match 'filter'

     projects
       List projects. Match 'filter'

     sas
       List service accounts for projects. Projects match 'filter'


__add__

    safire add

SYNOPSIS

    safire add COMMAND

DESCRIPTION

    Add projects, drives, service accounts(SAs), SA keys/jsons and group members

COMMANDS

    COMMAND is one of the following:

     apis
       Enables apis for projects. 'drive' and 'iam' apis by default. Automatic when projects are created but can be run manually also.

     drive
       Create a team/shared drive. Usage: 'safire add drive some_name'

     drives
       Create team/shared drives. Usage: 'safire add teamdrive some_filename' containing a list of drive names

     jsons
       Create and download json/key files to svcaccts folder. Add to TDs and/or groups.

     keys
       Create and download json/key files to svcaccts folder. Add to TDs and/or groups.

     members
       'add members' requires two arguments. Both 'project_filter' and 'group_filter' can be either the full project/group name or a partial name which matches some projects/groups. You can add SA emails from multiple projects to multiple groups if you wish.

     projects
       Create projects in authorized account. Usage: 'safire add projects 1'. Uses defaults in config if none specified.

     sas
       Create N service accounts/SAs in projects which match 'filter'. Usage: 'safire add sas 5 xyz' will add 5 SAs to all projects containing 'xys' if fewer than 100 exist. Will not overwrite SAs.

     user
       Add user (typically group name) to a shared/team drive. Usage: 'safire add someTDid mygroup@domain.com'


__delete__

NAME

    safire delete
    
SYNOPSIS

    safire delete COMMAND

DESCRIPTION

    Delete sas, jsons/keys, drives and group members. Note: 'remove' and 'delete' are equivalent commands

COMMANDS

    COMMAND is one of the following:

     drive
       Delete a team/shared drive. Usage: 'safire add teamdrive unique ID'. USE CAREFULLY! Does not work with non-empty drives.

     drives
       Delete team/shared drives. Usage: 'safire add teamdrive some_filename' with unique IDs. USE CAREFULLY

     jsons
       Remove json keys from svcaccts path

     members
       Remove members from groups. Match 'filter'

     sas
       Usage: 'safire remove sas filter' where filter is a string to match the projects from which you want to delete service accounts. To remove all SAs for all projects use "" as your filter

     user
       Remove user (typically group name) from a shared/team drive. Usage: 'safire remove someTDid mygroup@domain.com'



__auth__

NAME

    safire auth

SYNOPSIS

    safire auth GROUP | COMMAND

DESCRIPTION

    Authorize the app to access your projects, SAs, drives and groups. To generate creds.json go to https://developers.google.com/apps-script/api/quickstart/python , click Enable then download a json, rename it to creds.json and put a copy in the /creds folder

GROUPS

    GROUP is one of the following:

     scopes_all

     scopes_group

     scopes_proj

COMMANDS

    COMMAND is one of the following:

     all
       Create an auth token for adding/removing group members

     ask

     check

     groups
       Create an auth token for adding/removing group members

     projects
       Create an auth token for accessing and changing projects, service accounts, json keys and drives


__enable__

NAME

    safire enable

SYNOPSIS

    safire enable COMMAND

DESCRIPTION

    Add projects, drives, service accounts(SAs), SA keys/jsons and group members

COMMANDS

    COMMAND is one of the following:

     apis
       Enables apis for projects. 'drive' and 'iam' apis by default. Automatic when projects are created but can be run manually also.


__rename__

NAME

    safire rename

SYNOPSIS

    safire rename COMMAND

DESCRIPTION

    Rename json/key files to their email prefix, email numeric (omit prefix), uniqId or in a sequence. Usage: 'safire rename jsons email'  [choice email, email_seq, uniq, seq] Renaming is repeatable. Can always delete and redownload keys if needed.

COMMANDS

    COMMAND is one of the following:

     jsons
       Usage: 'safire rename jsons email'  [choice email, email_seq, uniq, seq]