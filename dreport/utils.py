# -*- coding: utf-8 -*-
#
import os
from .models.city import City, CityMonthRecord, CityPauseRecord
from django.core.exceptions import ObjectDoesNotExist
from docxtpl import DocxTemplate
from django.conf import settings
from datetime import datetime

TEMPLATE_DIR = os.path.join(settings.DEVICE_REPORT_DIR, 'WTSDtmp.docx')


class MonthRecordFunction(object):

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
                pause_count += 1
                if record.recovery_date_time:
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
        list_num = 1
        for risk in risks:
            if not risk.recovery_date_time:
                pause_time = 0
            else:
                pause_time = (risk.recovery_date_time - risk.risk_date_time).seconds
            risk_dict = {
                'Num': list_num,
                'city': record.city,
                'risk_date': risk.risk_date,
                'risk_time': risk.risk_date_time,
                'recovery_date_time': risk.recovery_date_time,
                'pause_time': pause_time,
                'text': risk.remark
            }
            list_num += 1
            risk_list.append(risk_dict)

        tpl = DocxTemplate(TEMPLATE_DIR)

        total_pause_time = int(int(record.total_pause_time) / 60)
        device_avarate = (1-(record.total_pause_time/(30 * 17.5 * 60 * 60))) * 100

        context = {
            'city': record.city.name,
            'year': year,
            'month': record.month,
            'device_count': parma.get('device', None),
            'total_error': record.pause_count,
            'error_time': total_pause_time,
            'error_date': '',
            'device_avarate': device_avarate,
            'text': parma.get('markdown', None),
            'form': risk_list,
        }
        tpl.render(context)
        report_path = os.path.join(settings.DEVICE_REPORT_DIR, '{}_{}.docx'.format(record.month, record.city.name))
        tpl.save(report_path)
        CityMonthRecord.save_report(record.id, '{}_{}.docx'.format(record.month, record.city.name))
        return report_path
