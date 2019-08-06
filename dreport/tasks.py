#  encoding: utf-8

import json
from datetime import datetime, timedelta

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.conf import settings

from common.utils import get_logger
from assets.models import Asset
from ops.celery import app as celery_app
from ops.celery.decorator import register_as_period_task
from dreport.models import CityPauseRecord
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
    hosts = [asset]
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


@celery_app.task
@register_as_period_task(crontab="0 1 * * *")
def collect_risk_as_period_task():
    from ops.utils import update_or_create_ansible_task

    period_task = None

    if not period_task:
        print("collect_risk_as_period_task pass")
        return

    try:
        rcs = Asset.objects.get(ip=settings.rcs_ip)
    except ObjectDoesNotExist as error:
        logger.error(error)
        return

    yestarday = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
    task_name = _("Collect city pause from rcs {}.".format(rcs.hostname))

    if settings.PERIOD_TASK != "on":
        print("Period task disabled, {} pass".format(task_name))
        logger.debug("Period task disabled, {} pass".format(task_name))
        return

    hosts = [rcs]
    tasks = const.COLLECT_PAUSE_TASKS

    print('CELERY 定时任务')
    print('开始从{}获取{}熔断信息'.format(rcs.hostname, yestarday))
    logger.info('开始从{}获取{}熔断信息'.format(rcs.hostname, yestarday))

    tasks[0]['action']['args'] = "python {}".format(settings.COLLECT_SCRIPT_PATH)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    if result[0]['ok']:
        data = result[0]['ok'][rcs.hostname]
        for key, value in data.items():
            stout = json.loads(value.get('stdout'))
            if CityPauseRecord().add_record(
                    risk_list=stout.get('risk_list', None),
                    risk_date=stout.get('date', None)
            ):
                print('添加成功')
                print(stout)
                logger.info('添加成功')
                logger.info(stout)
            else:
                print('添加失败')
                print(stout)
                logger.error('添加失败')
                logger.error(stout)