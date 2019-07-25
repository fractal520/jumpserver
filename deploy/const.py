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
        "name": "正在执行解压文件脚本",
        "action": {
            "module": "script",
            "args": "",
        }
    },
    {
        "name": "移除当前软连接",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "创建回滚版本软连接",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "修改文件所属权",
        "action": {
            "module": "script",
            "args": "",
        }
    },
    {
        "name": "重启应用",
        "action": {
            "module": "shell",
            "args": "",
        }
    }

]

CHECK_FILE_TASK = [
    {
        "name": "检查文件是否存在",
        "action": {
            "module": "shell",
            "args": ""
        }
    }
]


BACKUP_FILE = [
    {
        "name": "备份资产应用文件",
        "action": {
            "module": "script",
            "args": ""
        }
    }
]


COPY_FILE_TO_TASK = [
    {
        "name": "执行目录创建脚本",
        "action": {
            "module": "script",
            "args": ""
        }
    },
    {
        "name": "移除当前软连接",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "执行解压文件脚本",
        "action": {
            "module": "script",
            "args": ""
        }
    },
    {
        "name": "新建软连接",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "修改文件所属权",
        "action": {
            "module": "script",
            "args": "",
        }
    },
    {
        "name": "重启应用",
        "action": {
            "module": "shell",
            "args": "",
        }
    },
    {
        "name": "更新SuperVisor配置文件",
        "action": {
            "module": "shell",
            "args": "",
        }
    }
]
