#  encoding: utf-8
from celery import shared_task
from django.utils.translation import ugettext as _
from common.utils import get_logger
from . import const

logger = get_logger('jumpserver')


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
