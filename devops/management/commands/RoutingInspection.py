# !/usr/bin/env python
# encoding: utf-8
from datetime import datetime
from django.core.management.base import BaseCommand
from celery import shared_task
from common.utils import get_logger
from assets import const
from assets.models import Asset

logger = get_logger('jumpserver')
DATE_TIME = datetime.now()


@shared_task
def get_asset_hardware_info(assets):
    task_name = ("Daily routing inspection.Date: {}".format(DATE_TIME.strftime("%Y%m%d")))
    logger.info(task_name)
    return get_asset_hardware_info_util(assets=assets, task_name=task_name)


@shared_task
def get_asset_hardware_info_util(task_name, assets):
    from ops.utils import update_or_create_ansible_task
    hosts = [asset.fullname for asset in assets if asset.is_active and asset.is_unixlike()]
    tasks = const.UPDATE_ASSETS_HARDWARE_TASKS

    task, created = update_or_create_ansible_task(
        task_name, hosts=hosts, tasks=tasks, pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System',
    )

    result = task.run()

    genrate_routing_record(result)
    logger.debug(result)
    return result


@shared_task
def genrate_routing_record(result):
    pass


class Command(BaseCommand):

    def handle(self, *args, **options):
        assets = Asset.objects.all()
        result = get_asset_hardware_info(assets=assets)
        for hostname, value in result[0]['ok'].items():
            print(hostname)
            facts = value.get['setup']['invocation']['ansible_facts']
            print(facts)

