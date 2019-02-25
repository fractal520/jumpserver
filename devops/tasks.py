#  encoding: utf-8
import os
import json
from celery import shared_task
from django.utils.translation import ugettext as _
from django.conf import settings
from common.utils import get_logger
from ops.ansible.runner import get_default_options, PlayBookRunner
from ops.inventory import JMSInventory
from . import const

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


@shared_task
def ansible_install_role(role_name, roles_path):
    from ops.utils import update_or_create_ansible_task

    task_name = _('Install Ansible Role')

    hosts = ["localhost"]

    tasks = [{
        'name': 'Install Ansible Role {}'.format(role_name),
        'action': {
            'module': 'shell',
            'args': 'ansible-galaxy install --roles-path {} -f {}'.format(roles_path, role_name),
        }
    }]
    #: 新建一个任务列表  执行shell 任务

    task, created = update_or_create_ansible_task(
        task_name=task_name, hosts=hosts, tasks=tasks, pattern='localhost',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System',
    )
    result = task.run()

    summary = result[1]

    if summary.get('dark'):
        return False, summary['dark']
    else:
        return True, ""


# 使用playbook执行配置推送
@shared_task
def push_config_file(asset, playbook_name='test.yml', extra_vars=None):
    hostname_list = [asset.fullname]
    options = get_default_options()
    playbook_path = os.path.join(playbook_dir, playbook_name)
    logger.debug(playbook_path)
    if not playbook_name or not os.path.exists(playbook_path):
        raise FileNotFoundError('Please check playbook_path {}.'.format(playbook_name))
    options = options._replace(playbook_path=playbook_path)
    inventory = JMSInventory(hostname_list=hostname_list, run_as_admin=True, run_as=None, become_info=None)
    runner = PlayBookRunner(inventory=inventory, options=options)
    if extra_vars:
        runner.variable_manager.extra_vars = extra_vars
        logger.debug(json.dumps(runner.variable_manager.get_vars()))
    result = runner.run()
    logger.debug(result)
    return result
