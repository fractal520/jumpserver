# -*- coding: utf-8 -*-
#
import os
import xlwt
from .models.city import City, CityMonthRecord, CityPauseRecord, CityWeekRecord
from django.core.exceptions import ObjectDoesNotExist
from docxtpl import DocxTemplate
from django.conf import settings
from datetime import datetime

TEMPLATE_DIR = os.path.join(settings.DEVICE_REPORT_DIR, 'WTSDtmp.docx')
WEEK_TEMPLATE_DIR = os.path.join(settings.DEVICE_REPORT_DIR, 'WTSDtmp_week.docx')


class MonthRecordFunction(object):

    def batch_create(self, date):
        citys = City.objects.all()
        try:
            year = date.split('-')[0]
            month = date.split('-')[1]
        except BaseException as error:
            print(error)
            return False, str(error)

        for city in citys:
            records = CityPauseRecord.objects.filter(city=city, risk_date__month=month, risk_date__year=year)
            pause_count = 0
            total_pause_time = 0
            if records:
                for record in records:
                    if record.recovery_date_time:
                        pause_count += 1
                        total_pause_time += (record.recovery_date_time - record.risk_date_time).seconds
                    else:
                        total_pause_time += 0
                CityMonthRecord.create_or_update(city, month, pause_count, total_pause_time, year)
            else:
                print('该城市当月没有熔断记录')
                continue
        return True, 'success'

    def create(self, city_id, date):
        try:
            city = City.objects.get(id=city_id)
        except ObjectDoesNotExist as error:
            print(error)
            return False
        year = date.split('-')[0]
        month = date.split('-')[1]
        records = CityPauseRecord.objects.filter(city=city, risk_date__month=month, risk_date__year=year)
        pause_count = 0
        total_pause_time = 0
        if records:
            for record in records:
                if record.recovery_date_time:
                    pause_count += 1
                    total_pause_time += (record.recovery_date_time - record.risk_date_time).seconds
                else:
                    total_pause_time += 0
            CityMonthRecord.create_or_update(city, month, pause_count, total_pause_time, year)
            return True
        else:
            return False

    def report(self, parma):

        # print(parma)
        record_id = parma.get('id')
        record = CityMonthRecord.get_record(record_id)
        year = record.year
        risk_list = []
        risks = CityPauseRecord.objects.filter(city=record.city, risk_date__month=record.month, risk_date__year=year)
        risks = risks.order_by('-risk_date_time')
        list_num = 1
        for risk in risks:
            if not risk.recovery_date_time:
                continue

            pause_time = (risk.recovery_date_time - risk.risk_date_time).seconds/60
            recovery_date_time = datetime.strftime(risk.recovery_date_time.astimezone(), "%H:%M:%S")

            risk_dict = {
                'Num': list_num,
                'city': record.city,
                'risk_date': risk.risk_date,
                'risk_time': datetime.strftime(risk.risk_date_time.astimezone(), "%H:%M:%S"),
                'recovery_date_time': recovery_date_time,
                'pause_time': round(pause_time),
                'text': risk.remark
            }
            list_num += 1
            risk_list.append(risk_dict)

        tpl = DocxTemplate(TEMPLATE_DIR)

        total_pause_time = int(int(record.total_pause_time) / 60)
        device_avarate = (1-(record.total_pause_time/(30 * 17.5 * 60 * 60))) * 100
        default_markdown = "{0}后台网络波动，导致充值熔断".format(record.city.name)
        context = {
            'city': record.city.name,
            'year': year,
            'month': record.month,
            'device_count': parma.get('device', None),
            'total_error': record.pause_count,
            'error_time': total_pause_time,
            'error_date': '',
            'device_avarate': round(device_avarate, 2),
            'text': parma.get('markdown') if parma.get('markdown') else default_markdown,
            'form': risk_list,
        }
        tpl.render(context)
        report_path = os.path.join(settings.DEVICE_REPORT_DIR, '{}_{}.docx'.format(record.month, record.city.name))
        tpl.save(report_path)
        CityMonthRecord.save_report(record.id, '{}_{}.docx'.format(record.month, record.city.name))
        return report_path


class RiskRecord(object):

    def create(self, parm, time_quantum=False):
        if not time_quantum:
            year = parm.split('-')[0]
            month = parm.split('-')[1]
            records = CityPauseRecord.objects.filter(
                risk_date__month=month,
                risk_date__year=year,
                city__city_type__exact="CORPORATION"
            )
            filename = month
            ordering = '-risk_date_time'
        else:
            print(parm)
            print(time_quantum)
            filename = parm.get('start-date')+'to'+parm.get('end-date')
            records = CityPauseRecord.objects.filter(
                risk_date__gte=parm.get('start-date'),
                risk_date__lte=parm.get('end-date'),
                city__city_type__exact="CORPORATION"
            )
            ordering = '-risk_date_time'

        week_dict = {
                     'Monday': '星期一', 'Tuesday': '星期二',
                     'Wednesday': '星期三', 'Thursday': '星期四',
                     'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'
                     }
        save_address = settings.DEVICE_REPORT_DIR

        records = records.order_by(ordering)
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('records')
        titlestyle = xlwt.easyxf('pattern: pattern solid, fore_colour dark_green_ega;')
        name_list = ['编号', '城市', 'IP', '月 周', '故障日期', '星期', '故障时间', '恢复时间', '故障时长', '备注']

        colume_count = 0
        row_count = 0
        for name in name_list:
            worksheet.write(row_count, colume_count, name, titlestyle)
            colume_count += 1

        row_count += 1
        count = 1
        # datetime.strftime(risk.recovery_date_time.astimezone(), "%H:%M:%S")
        for record in records:
            if not record.recovery_date_time:
                continue
            worksheet.write(row_count, 0, count)
            count += 1
            worksheet.write(row_count, 1, record.city.name)
            worksheet.write(row_count, 2, '')
            worksheet.write(row_count, 3, '')
            worksheet.write(row_count, 4, datetime.strftime(record.risk_date, "%Y/%m/%d"))
            worksheet.write(row_count, 5, week_dict.get(datetime.strftime(record.risk_date, "%A")))
            worksheet.write(row_count, 6, datetime.strftime(record.risk_date_time.astimezone(), "%H:%M"))
            worksheet.write(row_count, 7, datetime.strftime(record.recovery_date_time.astimezone(), "%H:%M"))
            worksheet.write(
                row_count,
                8,
                str(round((record.recovery_date_time - record.risk_date_time).seconds / 60))+'分钟'
            )
            worksheet.write(row_count, 9, record.remark)
            row_count += 1

        workbook.save(os.path.join(save_address, filename + 'record.xls'))
        return filename + 'record.xls'


class WeekRecord(object):

    def create(self, date, week, city):
        # date = datetime.strptime(date, "%Y-%m-%d")
        week_record = CityWeekRecord()
        if city:
            week_record.create_record(date, week, citys=city)
            return True
        week_record.create_record(date, week)
        return True
