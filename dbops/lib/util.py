import random
import datetime


def workid() -> str:

    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    id = ''.join(random.sample('0123456789', 4))

    work_id = f'{now}{id}'
    return work_id
