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
        extra_vars=None,
        created_by="System",
        description="",
        ansible_role=None,
        run_as_admin=False,
        run_as=None
    ):

    # 判断是否传入playbook_name
    if not ansible_role:
        logger.error("ansible role can't be None.")
        return False

    if not task_name:
        task_name = ansible_role

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
    task.assets.set(assets)
    task.save()

    return task


# 将timestamp转换成当地时间字符串格式
def translate_timestamp(timestamp):

    time_array = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_array)
