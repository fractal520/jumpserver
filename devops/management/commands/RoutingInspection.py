# !/usr/bin/env python
# encoding: utf-8
import os
import json
import xlwt
from datetime import datetime
import datetime as dtime
from django.core.management.base import BaseCommand
from django.conf import settings
from celery import shared_task
from common.utils import get_logger
from assets import const
from assets.models import Asset
from contextlib import suppress


logger = get_logger('jumpserver')
DATE_TIME = datetime.now()
MONTH = "{}月".format(DATE_TIME.strftime("%m").replace("0", ""))
# 本地存档
ROUTING_INSPECTION_DATA_PATH = settings.ROUTING_INSPECTION_DATA_PATH
# 运维samba归档
ROUTING_INSPECTION_FILE_SAVE = settings.ROUTING_INSPECTION_FILE_SAVE

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

    return genrate_routing_record(result)


@shared_task
def genrate_routing_record(result):
    data_list = []
    if not result[0]['ok']:
        logger.info(result[0])
        logger.debug(result)
        return False
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
        data_list.append(host_data)
        logger.info('获取到{}的巡检数据'.format(host_data['hostname']))
    return data_list


class DataWriter(object):

    @staticmethod
    def local_save(data_list):
        file_name = os.path.join(ROUTING_INSPECTION_DATA_PATH, DATE_TIME.strftime('%Y%m%d') + '.txt')
        with open(file_name, 'wt') as info:
            logger.info('开始写入数据')
            for data in data_list:
                info.write(json.dumps(data)+'\n')
        if not os.path.isfile(file_name):
            raise FileNotFoundError('数据文件不存在,请重新生成。')

    @staticmethod
    def remote_file_save(data_list):
        host = '巡检记录'
        line_count = 1
        row_count = 0
        name_list = ['ID', 'hostname', 'IPaddress', 'date', 'uptime', 'processor_count', 'Total_Mem', 'Used_mem',
                     'Free_mem']
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet(host)
        worksheet.col(0).width = 1000
        worksheet.col(1).width = 4500
        worksheet.col(4).width = 4500
        titlestyle = xlwt.easyxf('pattern: pattern solid, fore_colour dark_green_ega;')
        warnstyle = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
        for name in name_list:
            worksheet.write(0, row_count, name, titlestyle)
            row_count += 1
        for line_dict in data_list:
            worksheet.write(line_count, 0, line_count)
            worksheet.write(line_count, 1, line_dict.get('hostname'))
            worksheet.write(line_count, 2, line_dict.get('IP'))
            worksheet.write(line_count, 3, datetime.now().strftime('%Y%m%d'))
            worksheet.write(line_count, 4, line_dict.get('ansible_uptime_seconds'))
            worksheet.write(line_count, 5, line_dict.get('cpu_processor_count'))
            worksheet.write(line_count, 6, str(line_dict.get('mb_total')) + 'MB')
            worksheet.write(line_count, 7, str(line_dict.get('mb_use')) + 'MB')
            worksheet.write(line_count, 8, str(line_dict.get('mb_free')) + 'MB')
            row = 9
            for key, value in line_dict.get('disk_dict').items():
                try:
                    with suppress(BaseException):
                        worksheet.write(0, row, 'disk_name', titlestyle)
                    worksheet.write(line_count, row, key)
                    row += 1

                    with suppress(BaseException):
                        worksheet.write(0, row, 'disk_size_total', titlestyle)
                    disk_size_total = int(value.get('disk_size_total') / 1024 / 1024)
                    worksheet.write(line_count, row, str(disk_size_total) + 'MB')
                    row += 1

                    with suppress(BaseException):
                        worksheet.write(0, row, 'disk_size_avail', titlestyle)
                    disk_size_avail = int(value.get('disk_size_avail') / 1024 / 1024)
                    worksheet.write(line_count, row, str(disk_size_avail) + 'MB')
                    row += 1

                    with suppress(BaseException):
                        worksheet.write(0, row, 'disk_use', titlestyle)
                    disk_use = int(100 * (1 - (int(value.get('disk_size_avail') / 1024 / 1024) / int(
                        value.get('disk_size_total') / 1024 / 1024))))
                    if disk_use >= 70:
                        worksheet.write(line_count, row, str(disk_use) + '%', warnstyle)
                        row += 1
                    else:
                        worksheet.write(line_count, row, str(disk_use) + '%')
                        row += 1
                except BaseException as e:
                    print(e, line_dict.get('hostname'))
            line_count += 1
        wb_name = host+DATE_TIME.strftime('%Y%m%d')+'.xls'
        wb_path = os.path.join(
            ROUTING_INSPECTION_FILE_SAVE,
            DATE_TIME.strftime("%Y"),
            MONTH,
            DATE_TIME.strftime("%Y%m%d"),
            wb_name
        )
        workbook.save(wb_path)


class Command(BaseCommand):

    def handle(self, *args, **options):
        assets = Asset.objects.order_by('hostname')
        data_list = get_asset_hardware_info(assets=assets)
        if not data_list:
            logger.error('没有获取到巡检数据，请手动检查。')
            return False
        try:
            DataWriter.local_save(data_list)
            local_result = True
        except FileNotFoundError as error:
            local_result = None
            logger.error(str(error))

        if local_result:
            try:
                DataWriter.remote_file_save(data_list)
            except BaseException as error:
                logger.error(str(error))
