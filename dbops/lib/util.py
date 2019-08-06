import random
import datetime
import os
import re


def workid() -> str:

    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    id = ''.join(random.sample('0123456789', 4))

    work_id = f'{now}{id}'
    return work_id


def get_sql_path(dirname, key_words=r'.sql$'):
    sql_path_list = []
    for root, dirs, files in os.walk(dirname):
        for f in files:
            apath = os.path.join(root, f)
            if re.search(key_words, f):
                sql_path_list.append(apath)
    return sql_path_list
