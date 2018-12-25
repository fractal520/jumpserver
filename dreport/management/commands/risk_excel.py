#  !/usr/bin/env python

import xlwt
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from dreport.models.city import CityPauseRecord


class Command(BaseCommand):

    def handle(self, *args, **options):
        data_month = input('请输入你要获取的熔断月份: ')
        week_dict = {
                     'Monday': '星期一', 'Tuesday': '星期二',
                     'Wednesday': '星期三', 'Thursday': '星期四',
                     'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'
                     }
        save_address = '/scss/jms/jumpserver/data/report/'
        records = CityPauseRecord.objects.filter(risk_date__month=data_month)
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('records')
        titlestyle = xlwt.easyxf('pattern: pattern solid, fore_colour dark_green_ega;')
        name_list = ['城市', '', '故障日期', '星期', '故障时间', '恢复时间', '故障时长', '备注']

        colume_count = 0
        row_count = 0
        for name in name_list:
            worksheet.write(row_count, colume_count, name, titlestyle)
            colume_count += 1

        row_count += 1

        for record in records:
            worksheet.write(row_count, 0, record.city.name)
            worksheet.write(row_count, 1, '')
            worksheet.write(row_count, 2, datetime.strftime(record.risk_date, "%Y/%m/%d"))
            worksheet.write(row_count, 3, week_dict.get(datetime.strftime(record.risk_date, "%A")))
            # worksheet.write(row_count, 4, datetime.strftime(record.risk_date, "%A"))
            worksheet.write(row_count, 4, datetime.strftime(record.risk_date_time, "%H:%M"))
            if record.recovery_date_time:
                worksheet.write(row_count, 5, datetime.strftime(record.recovery_date_time, "%H:%M"))
                worksheet.write(
                    row_count,
                    6,
                    str(round((record.recovery_date_time - record.risk_date_time).seconds / 60))+'分钟'
                )
            else:
                worksheet.write(row_count, 5, None)
                worksheet.write(row_count, 6, None)
            worksheet.write(row_count, 7, record.remark)
            row_count += 1

        workbook.save(os.path.join(save_address, data_month + 'record.xls'))
