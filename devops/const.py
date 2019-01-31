#  encoding: utf-8

TASK_OPTIONS = {
    'timeout': 10,
    'forks': 10,
}

PUSH_FILE_TASK = [
    {
        'name': 'push file to asset',
        'action': {
            "module": "copy",
            "args": "",
        }
    }
]