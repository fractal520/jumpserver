#  encoding: utf-8

from celery import shared_task
from django.utils.translation import ugettext as _
from common.utils import get_logger
from . import const

logger = get_logger('jumpserver')


# collect city risk from rcs logs
@shared_task
def collect_risk_manual(asset, script_path=None):
    task_name = _("Collect city pause from rcs {}.".format(asset.hostname))
    return collect_risk_util(asset, task_name, script_path)


@shared_task
def collect_risk_util(asset, task_name, script_path):
    from ops.utils import update_or_create_ansible_task
    hosts = [asset.fullname]
    tasks = const.COLLECT_PAUSE_TASKS
    tasks[0]['action']['args'] = "python {}".format(script_path)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    return result
