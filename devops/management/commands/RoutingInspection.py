# !/usr/bin/env python
# encoding: utf-8
from datetime import datetime
import datetime as dtime
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
            facts = value['setup']['ansible_facts']
            ansible_uptime_seconds = str(dtime.timedelta(seconds=facts.get('ansible_uptime_seconds')))
            cpu_processor_count = facts.get('ansible_processor_count')
            hostname = facts.get('ansible_hostname')
            IP = facts.get('ansible_default_ipv4').get('address')
            mb_total = facts.get('ansible_memory_mb').get('real').get('total')
            mb_use = facts.get('ansible_memory_mb').get('real').get('used')
            mb_free = facts.get('ansible_memory_mb').get('real').get('free')
            disk_dict = {}
            for disk in facts.get('ansible_mounts'):
                disk_device = disk.get('device')
                disk_size_total = disk.get('size_total')
                disk_size_avail = disk.get('size_available')
                d_d = {disk_device: {'disk_size_total': disk_size_total, 'disk_size_avail': disk_size_avail}}
                disk_dict.update(d_d)
            # print(mb_total)
            host_data = {'cpu_processor_count': cpu_processor_count, 'ansible_uptime_seconds': ansible_uptime_seconds,
                         'hostname': hostname, 'IP': IP, 'mb_total': mb_total, 'mb_use': mb_use, 'mb_free': mb_free,
                         'disk_dict': disk_dict}
            print(host_data)
