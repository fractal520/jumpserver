# encoding: utf-8
import os
import time
import json
import xlwt
from datetime import datetime
import datetime as dtime
from contextlib import suppress
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


# 本地存档
ROUTING_INSPECTION_DATA_PATH = settings.ROUTING_INSPECTION_DATA_PATH
# 运维samba归档
ROUTING_INSPECTION_FILE_SAVE = settings.ROUTING_INSPECTION_FILE_SAVE
MONTH = "{}月".format(datetime.now().strftime("%m").replace("0", ""))


def genrate_routing_record(result):
    data_list = []
    if not result[0]['ok']:
        logger.info(result[0])
        logger.debug(result)
        return False
    if result[1]['dark']:
        for k, v in result[1]['dark'].items():
            logger.info('{}无法收集巡检数据，原因是{}'.format(k, json.dumps(v)))

    for hostname, value in result[0]['ok'].items():
        facts = value['setup']['ansible_facts']
        ansible_uptime_seconds = str(dtime.timedelta(seconds=facts.get('ansible_uptime_seconds')))
        # cpu_processor_count = facts.get('ansible_processor_count')
        cpu_processor_count = "{}*{}".format(facts.get('ansible_processor_count'), facts.get('ansible_processor_cores'))
        hostname = facts.get('ansible_hostname')
        IP = facts.get('ansible_default_ipv4').get('address')
        mb_total = facts.get('ansible_memory_mb').get('real').get('total')
        mb_use = facts.get('ansible_memory_mb').get('real').get('used')
        mb_free = facts.get('ansible_memory_mb').get('real').get('free')
        disk_dict = {}
        if facts.get('ansible_mounts'):
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
        file_name = os.path.join(ROUTING_INSPECTION_DATA_PATH, datetime.now().strftime('%Y%m%d') + '.txt')
        with open(file_name, 'wt') as info:
            print('开始写入数据')
            logger.info('开始写入数据')
            for data in data_list:
                info.write(json.dumps(data)+'\n')
        if not os.path.isfile(file_name):
            print('数据文件不存在,请重新生成。')
            raise FileNotFoundError('数据文件不存在,请重新生成。')
        print('数据写入成功')
        logger.info('数据写入成功')

    @staticmethod
    def remote_file_save(data_list):
        host = '巡检记录'
        line_count = 1
        row_count = 0
        # 表格首行字段定义
        name_list = ['ID', 'hostname', 'IPaddress', 'date', 'uptime', 'processor_count', 'Total_Mem', 'Used_mem',
                     'Free_mem']
        # 表格相关设置
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet(host)
        worksheet.col(0).width = 1000
        worksheet.col(1).width = 4500
        worksheet.col(4).width = 4500
        titlestyle = xlwt.easyxf('pattern: pattern solid, fore_colour dark_green_ega;')
        warnstyle = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
        # 写首行字段
        for name in name_list:
            worksheet.write(0, row_count, name, titlestyle)
            row_count += 1
        # 写巡检数据
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
            if not line_dict.get('disk_dict'):
                continue
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
        wb_name = host+datetime.now().strftime('%Y%m%d')+'.xls'

        # 生成当日归档目录路径
        save_dir = os.path.join(
                ROUTING_INSPECTION_FILE_SAVE, datetime.now().strftime("%Y"),
                MONTH, datetime.now().strftime("%Y%m%d")
        )

        # 判断该巡检归档目录是否存在如果不存在则自动创建
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir, mode=0o755)

        # 保存巡检归档表格
        wb_path = os.path.join(save_dir, wb_name)
        workbook.save(wb_path)
        return wb_path
