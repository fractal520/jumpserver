# encoding: utf-8
import os
import time
from django.conf import settings
from common.utils import get_logger
from .models import AnsibleRole, PlayBookTask

logger = get_logger('jumpserver')


def create_playbook_task(
        assets,
        task_name="",
        playbook_name=None,
        extra_vars=None,
        created_by=None,
        description="",
        ansible_role=None,
        run_as_admin=False,
        run_as=None
    ):

    """
    :param run_as:
    :param run_as_admin:
    :type ansible_role: object
    :param description:
    :param created_by:
    :param assets: 传入assets的full_hostname_list [asset.fullname,]
    :param task_name: 这个playbook_task的名称
    :param playbook_name: just like 'test.yml'
    :param extra_vars: 如果playbook需要额外的变量要在这里定义 {'varsname': varsvalue}
    """

    # 判断是否传入playbook_name
    if not playbook_name:
        logger.error("playbook_name can't be None.")
        return False

    if not task_name:
        task_name = playbook_name

    defaults = {
        'name': task_name,
        'created_by': created_by,
        'desc': description,
        'ansible_role': ansible_role,
        'run_as_admin': run_as_admin,
        'run_as': run_as,
        'extra_vars': extra_vars
    }

    PlayBookTask.objects.update_or_create(name=task_name, defaults=defaults)
    task = PlayBookTask.objects.get(name=task_name)
    task.hosts = assets
    task.save()

    return task


# 将timestamp转换成当地时间字符串格式
def translate_timestamp(timestamp):

    time_array = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_array)
