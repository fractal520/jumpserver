#  encoding: utf-8
import os
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext as _
from common.utils import get_logger
from . import const

logger = get_logger('jumpserver')


# collect city risk from rcs logs
@shared_task
def collect_risk_manual(asset, log_path=None):
    task_name = _("Collect city pause from {} {}.".format(asset.hostname, log_path))
    return collect_risk_util(asset, log_path, task_name)


@shared_task
def collect_risk_util(asset, log_path, task_name):
    from ops.utils import update_or_create_ansible_task
    hosts = [asset.fullname]
    tasks = const.COLLECT_PAUSE_TASKS
    tasks[0]['action']['args'] = "python /home/zhangwj/RA.py"
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    return result
