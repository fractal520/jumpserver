# encoding: utf-8
import os
import json
import time
from django.conf import settings
from common.utils import get_logger
from ops.ansible.runner import get_default_options, PlayBookRunner
from ops.inventory import JMSInventory

logger = get_logger('jumpserver')
playbook_dir = os.path.join(settings.PROJECT_DIR, 'data', 'playbooks')

if not os.path.isdir(playbook_dir):
    os.makedirs(playbook_dir)


def create_playbook_task(asset, playbook_name=None, extra_vars=None):

    # 判断是否传入playbook_name
    if not playbook_name:
        logger.error("playbook_name can't be None.")
        return False

    playbook_path = os.path.join(playbook_dir, playbook_name)
    logger.debug(playbook_path)

    # 判断playbook是否存在
    if not os.path.exists(playbook_path):
        raise FileNotFoundError('Please check playbook_path {}.'.format(playbook_name))

    # 获取默认options
    options = get_default_options()
    # 修改默认options中的playbook_path
    options = options._replace(playbook_path=playbook_path)

    # 使用JMSInventory构建inventory
    inventory = JMSInventory(hostname_list=[asset.fullname], run_as_admin=True, run_as=None, become_info=None)

    # 构建出runner
    runner = PlayBookRunner(inventory=inventory, options=options)

    # 如果传入了额外变量则加到runner里
    if extra_vars:
        runner.variable_manager.extra_vars = extra_vars
        logger.debug(json.dumps(runner.variable_manager.get_vars()))

    return runner


# 将timestamp转换成当地时间字符串格式
def translate_timestamp(timestamp):

    time_array = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_array)
