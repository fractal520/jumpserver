#  encoding: utf-8

TASK_OPTIONS = {
    'timeout': 10,
    'forks': 10,
}

COLLECT_PAUSE_TASKS = [
    {
        "name": "collect city pause",
        "action": {
            "module": "shell",
            "args": "",
        }
    }
]