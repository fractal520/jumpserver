#  encoding: utf-8
import os
import json
from datetime import datetime

from celery import shared_task, subtask
from celery.schedules import crontab
from django.utils.translation import ugettext as _
from django.conf import settings

from assets import const as assets_const
from assets.models import Asset
from common.utils import get_logger, get_object_or_none
from ops.models import Task
from ops.celery import app as celery_app
from ops.celery.decorator import register_as_period_task
from devops.utils import create_playbook_task, genrate_routing_record, DataWriter
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


@shared_task
def run_ansible_task(tid, callback=None, **kwargs):
    """
    :param tid: is the tasks serialized data
    :param callback: callback function name
    :return:
    """
    task = get_object_or_none(Task, id=tid)
    if task:
        result = task.run()
        if callback is not None:
            subtask(callback).delay(result, task_name=task.name)
        return result
    else:
        logger.error("No task found")


@shared_task
def routing_inspection_manual():
    return routing_inspection_util(manual=True)


@celery_app.task
@register_as_period_task(crontab="0 2 * * *")
def routing_inspection_util(manual=False):
    task_name = ("Daily routing inspection as period task.Date: {}".format(datetime.now().strftime("%Y%m%d")))
    if manual:
        print('run task manual')
    else:
        if settings.PERIOD_TASK != "on":
            print("Period task disabled, {} pass".format(task_name))
            logger.debug("Period task disabled, {} pass".format(task_name))
            return "Period task disabled, {} pass".format(task_name)
    from ops.utils import update_or_create_ansible_task
    hosts = [asset for asset in Asset.objects.all() if asset.is_active and asset.is_unixlike()]
    tasks = assets_const.UPDATE_ASSETS_HARDWARE_TASKS

    task, created = update_or_create_ansible_task(
        task_name, hosts=hosts, tasks=tasks, pattern='all',
        options=assets_const.TASK_OPTIONS, run_as_admin=True, created_by='System',
    )

    result = task.run()
    data_list = genrate_routing_record(result)
    if not data_list:
        print('没有获取到巡检数据，请手动检查。')
        logger.error('没有获取到巡检数据，请手动检查。')
        return False
    try:
        DataWriter.local_save(data_list)
        local_result = True
    except FileNotFoundError as error:
        local_result = None
        print(str(error))
        logger.error(str(error))

    if local_result:
        print('开始生成excel文件')
        logger.info('开始生成excel文件')
        try:
            wb_path = DataWriter.remote_file_save(data_list)
            print('生成成功，保存路径为{}。'.format(wb_path))
            logger.info('生成成功，保存路径为{}。'.format(wb_path))
        except BaseException as error:
            logger.error(str(error))

    return True


"""
@celery_app.task
def test_func(x, y):
    print('开始测试任务')
    print(x + y)
"""
