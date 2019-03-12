#  encoding: utf-8
import os
import json
from celery import shared_task, subtask
from django.utils.translation import ugettext as _
from django.conf import settings
from common.utils import get_logger, get_object_or_none
from devops.utils import create_playbook_task
from devops import const
from devops.models import PlayBookTask

logger = get_logger('jumpserver')
playbook_dir = os.path.join(settings.PROJECT_DIR, 'data', 'playbooks')


# push file to asset
@shared_task
def push_file_manual(asset, dest_path=None, file_path=None):
    task_name = _("push_file_manual {}.".format(asset.hostname))
    return push_file_util(asset, dest_path, task_name, file_path)


@shared_task
def push_file_util(asset, dest_path, task_name, file_path):
    from ops.utils import update_or_create_ansible_task
    logger.info("start push {} to {}:{}".format(file_path, asset.ip, dest_path))
    hosts = [asset.fullname]
    tasks = const.PUSH_FILE_TASK
    tasks[0]['action']['args'] = "src={0} dest={1}".format(file_path, dest_path)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()
    if result[0]['ok']:
        logger.info("push {} to {}:{} successful".format(file_path, asset.ip, dest_path))
    else:
        print(asset.ip + 'failed')
        logger.error("push {} to {}:{} failed".format(file_path, asset.ip, dest_path))
    return True


# 执行ansible-playbook
@shared_task
def execute_playbook(asset, playbook_name=None, extra_vars=None):
    runner = create_playbook_task(asset, playbook_name, extra_vars)
    result = runner.run()
    logger.debug(result)
    return result


@shared_task
def run_ansible_playbook(tid, callback=None, **kwargs):
    """
    :param tid: is the tasks serialized data
    :param callback: callback function name
    :return:
    """
    task = get_object_or_none(PlayBookTask, id=tid)
    if task:
        result = task.run()
        if callback is not None:
            subtask(callback).delay(result, task_name=task.name)
        return result
    else:
        logger.error("No task found")


def reset_task_playbook_path(tid):
    task = get_object_or_none(PlayBookTask, id=tid)
    result = task.create_playbook(task.ansible_role)
    if result:
        return True
    else:
        logger.error('Reset playbook path failed!')
        return False
