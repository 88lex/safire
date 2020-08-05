
**SAFIRE**
^^^^^^^^^^^^^^

A flexible tool to create and delete GSuite projects, service accounts and jsons which can be used with shared/team drives.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install safire from either `pypi <https://pypi.org/project/safire/>`_ or `github <https://github.com/88lex/safire>`_

After installing but before using safire you must 


* create a creds.json file
* run both ``safire auth projects`` and ``safire auth groups`` to create token.pickle and grptoken.pickle

  * Creating two tokens allows you to use different accounts for creating projects/SAs and creating group(s)

* Leram, see below for further details :-)

**BONUS**\ :  ``safire list all`` will create both csv and xlsx files listing name/unique id/etc. 
for all projects, service accounts, shared drives, groups and group members for your account. 
Handy for use with other apps and scripts.


* Simple usage syntax: e.g. ``safire list projects``
* 
  Available main commands:


  * list
  * add / create
  * remove / delete
  * auth
  * enable
  * rename

* 
  Most commands will tell you which subcommands are available by simply typing the main command with no flags. 
  e.g. ``safire list`` or optionally ``safire list -h`` . Subcommands include:


  * projects
  * sas - aka service accounts
  * keys / jsons
  * groups
  * members
  * drives (yes, safire can create and delete shared drives)

* 
  User configuration information such as project name/prefix, number of projects to create, service account prefix 
  and so on are in the ``config.py`` file in the /safire/safire folder.


  * All options can be set in either the config.py or via command line flags (-h or --help for any commands)
  * If you install with pip then you can find the location of config.py with ``pip list -v | grep safire``\ , then edit as needed

* 
  Credential files and files created by safire are by default in the user home (~ in linux) directory under 
  safire/creds, safire/data and safire/svcaccts. This location can be changed in config.py

* 
  NOTE: Commands below are in the format ``safire command subcommand`` This assumes you pip install the script. 
  You can run it directly without installing by navigating to /safire/safire and using ``./safire.py command subcommand``

**Several ways to install/use safire**\ : 


* Recommended: Python 3.6.1 or higher
* ``pip install safire`` will install from pypi.org

  * Or I like `pipx <https://github.com/pipxproject/pipx>`_ for a virtual env install with\ ``pipx install safire``

* 
  You can run safire directly after cloning from github using ``safire.py`` 
  (Note that safire.py in two levels down: ``cd /opt/safire/safire``\ ; ``./safire.py list projects``\ ) 


  * If running manually, first run ``pip install -r requirements.txt`` to get dependencies installed

* 
  For advanced or adventurous users there are other options to run safire from anywhere on your machine.
  e.g. using `poetry <https://python-poetry.org/>`_\ , virtual env installs or directly using ``pip install .``


  * For example to pip install locally:

    * Navigate to to the base /safire dir where you git cloned safire (/safire, not /safire/safire) 
    * Use a recent version of pip that runs with pyproject.toml rather than setup.py 
      [I just added setup.py, might help] 
    * If you want to upgrade pip use ``pip install --upgrade pip`` or ``sudo -H pip3 install --upgrade pip``
    * From your /safire folder run ``pip install .``  If successful then you should now be able to run safire everywhere

**Apologies:** Python dependencies are complex in different environments. Bear with me as I try to make installs easier.

**Setup of safire**

Before running safire you will need one gsuite project (new or old is fine) with several apis enabled.


* If no project exists go to https://console.cloud.google.com/projectcreate to create one in your main gsuite account
* 
  Then go to https://console.cloud.google.com/apis/library. Ensure you choose your main project (dropdown at the top 
  of the page), then enable the following APIs:

    [ **You only need to do this once.** ]


  * Admin SDK
  * Google Drive API
  * Identity and Access Management (IAM) API
  * Cloud Resource Manager API
  * Service Usage API
  * Service Management API

Once you have enabled the above APIs then go to this page 


* https://console.cloud.google.com/apis/credentials
* Click Create Credentials
* Choose ``OAuth client ID``
* For Application type choose ``Desktop app`` and name it as you like ( 'safire' or anything)
* Click Create
* Finally choose ``Download JSON``
* You will use this JSON to create a token which allows you access to your account and gives you permission to 
  create projects, service accounts, etc. 

  * Keep one copy of this JSON in a safe place, then put a copy named ``creds.json`` in the ``~/safire/creds`` 
    folder [specified in your config.py file - you can change the location if you like]

Once you have this initial project created, all the APIs above enabled and have created/downloaded the credentials 
creds.json you are ready to use safire.

The command line is very flexible. You can quickly and easily 


* create projects via ``safire add projects 5`` will add 5 projects
* create and delete service accounts(SAs) via ``safire add sas proj000`` will add 
* create and delete json keys (that let you access shared drives and copy/sync/move files)
* add the SA emails to groups and shared drives to use with tools like sasync, cloudplow/cloudbox, crop etc.  

``Don't be afraid to play with the commands. You can fix almost anything by deleting and recreating components 
in a few minutes.  [The exception being projects, which you should not delete as they go into a 30-day holding 
bin before being fully deleted, and count against your project quota.]``

A typical, simple flow to use safire: 


* download a credentials json 
* create auth token to enable safire to access your account: ``safire auth all`` will create two tokens, one 
  to access projects/drives/etc and one to access groups 
* add projects: ``safire add projects 5`` will add 5 projects using the prefix in your config.py file
* enable apis: happens automatically when you add projects, but can be done manually
* create sas: ``safire add sas ""`` will add sas to all or your projects using # of SAs in config.py 
* download json keys: ``safire add jsons ""`` will create and download service account json keys to the folder in config.py
* add members to group: ``safire add members "" mygroup@domain.com`` will add all SA emails from all projects 
  to a group called mygroup@domain.com
* add group to shared (team) drive

Detailed commands
-----------------

**list**

.. code-block::

   safire list


SYNOPSIS

.. code-block::

   safire list COMMAND


DESCRIPTION

.. code-block::

   List drives, projects, service accounts (SAs), SA json keys, groups and group members. 
   In most cases a filter can be applied.


COMMANDS

.. code-block::

   COMMAND is one of the following:

    all
      List all drives, projects, service accounts, json keys, groups and group members. Also exports 
      these lists with full data fields to csv and xlsx files in data_path folder

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



**add**

.. code-block::

   safire add


SYNOPSIS

.. code-block::

   safire add COMMAND


DESCRIPTION

.. code-block::

   Add projects, drives, service accounts(SAs), SA keys/jsons and group members


COMMANDS

.. code-block::

   COMMAND is one of the following:

    apis
      Enables apis for projects. 'drive' and 'iam' apis by default. Automatic when projects are 
      created but can be run manually also.

    drive
      Create a team/shared drive. Usage: 'safire add drive some_name'

    drives
      Create team/shared drives. Usage: 'safire add teamdrive some_filename' containing a list of drive names

    jsons
      Create and download json/key files to svcaccts folder. Add to TDs and/or groups.

    keys
      Create and download json/key files to svcaccts folder. Add to TDs and/or groups.

    members
      'add members' requires two arguments. Both 'project_filter' and 'group_filter' can be either the 
      full project/group name or a partial name which matches some projects/groups. 
      You can add SA emails from multiple projects to multiple groups if you wish.

    projects
      Create projects in authorized account. Usage: 'safire add projects 1'. Uses defaults in config if none specified.

    sas
      Create N service accounts/SAs in projects which match 'filter'. Usage: 'safire add sas 5 xyz' will 
      add 5 SAs to all projects containing 'xys' if fewer than 100 exist. Will not overwrite SAs.

    user
      Add user (typically group name) to a shared/team drive. Usage: 'safire add someTDid mygroup@domain.com'



**delete**

NAME

.. code-block::

   safire delete


SYNOPSIS

.. code-block::

   safire delete COMMAND


DESCRIPTION

.. code-block::

   Delete sas, jsons/keys, drives and group members. Note: 'remove' and 'delete' are equivalent commands


COMMANDS

.. code-block::

   COMMAND is one of the following:

    drive
      Delete a team/shared drive. Usage: 'safire add teamdrive unique ID'. USE CAREFULLY! 
      Does not work with non-empty drives.

    drives
      Delete team/shared drives. Usage: 'safire add teamdrive some_filename' with unique IDs. USE CAREFULLY

    jsons
      Remove json keys from svcaccts path

    members
      Remove members from groups. Match 'filter'

    sas
      Usage: 'safire remove sas filter' where filter is a string to match the projects from which you want 
      to delete service accounts. To remove all SAs for all projects use "" as your filter

    user
      Remove user (typically group name) from a shared/team drive. Usage: 'safire remove someTDid mygroup@domain.com'




**auth**

NAME

.. code-block::

   safire auth


SYNOPSIS

.. code-block::

   safire auth GROUP | COMMAND


DESCRIPTION

.. code-block::

   Authorize the app to access your projects, SAs, drives and groups. To generate creds.json go 
   to https://developers.google.com/apps-script/api/quickstart/python , click Enable then download a json, 
   rename it to creds.json and put a copy in the /creds folder


GROUPS

.. code-block::

   GROUP is one of the following:

    scopes_all

    scopes_group

    scopes_proj


COMMANDS

.. code-block::

   COMMAND is one of the following:

    all
      Create an auth token for adding/removing group members

    ask

    check

    groups
      Create an auth token for adding/removing group members

    projects
      Create an auth token for accessing and changing projects, service accounts, json keys and drives



**enable**

NAME

.. code-block::

   safire enable


SYNOPSIS

.. code-block::

   safire enable COMMAND


DESCRIPTION

.. code-block::

   Add projects, drives, service accounts(SAs), SA keys/jsons and group members


COMMANDS

.. code-block::

   COMMAND is one of the following:

    apis
      Enables apis for projects. 'drive' and 'iam' apis by default. Automatic when projects 
      are created but can be run manually also.



**rename**

NAME

.. code-block::

   safire rename


SYNOPSIS

.. code-block::

   safire rename COMMAND


DESCRIPTION

.. code-block::

   Rename json/key files to their email prefix, email numeric (omit prefix), uniqId or in a sequence. 
   Usage: 'safire rename jsons email'  [choice email, email_seq, uniq, seq] Renaming is repeatable. 
   Can always delete and redownload keys if needed.


COMMANDS

.. code-block::

   COMMAND is one of the following:

    jsons
      Usage: 'safire rename jsons email'  [choice email, email_seq, uniq, seq]




CREDITS:
--------

   Many ideas, some bits of code and inspiration from spazzlo, fionera and generally from l3uddz, 
   ncw and others - all of whose projects are excellent and some of them do some/all of what safire does. 
   If I forgot to mention you here let me know.

   Thanks for testing by max, sk and recently by leram, jonfinley, 1activegeek and their posse
