#  encoding: utf-8

TASK_OPTIONS = {
    'timeout': 10,
    'forks': 10,
}

TEST_CONN_TASKS = [
    {
        "name": "ping",
        "action": {
            "module": "ping",
            "args": "",
        }
    }
]

ROLLBACK_TASK = [
    {
        "name": "shell script compress backup.",
        "action": {
            "module": "script",
            "args": "",
        }
    },
    {
        "name": "remove link",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "create old_version link",
        "action": {
            "module": "file",
            "args": "",
        }
    }

]

CHECK_FILE_TASK = [
    {
        "name": "CHECK_FILE_EXIST",
        "action": {
            "module": "shell",
            "args": ""
        }
    }
]


BACKUP_FILE = [
    {
        "name": "backup asset app file",
        "action": {
            "module": "script",
            "args": ""
        }
    }
]


COPY_FILE_TO_TASK = [
    {
        "name": "create dir script",
        "action": {
            "module": "script",
            "args": ""
        }
    },
    {
        "name": "copy tar file to asset",
        "action": {
            "module": "copy",
            "args": ""
        }
    },
    {
        "name": "remove link",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "compress tar script",
        "action": {
            "module": "script",
            "args": ""
        }
    },
    {
        "name": "create new link",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "script",
        "action": {
            "module": "script",
            "args": "",
        }
    },
    {
        "name": "shell",
        "action": {
            "module": "shell",
            "args": "",
        }
    },
    {
        "name": "shell",
        "action": {
            "module": "shell",
            "args": "",
        }
    }
]
