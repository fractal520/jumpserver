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
        print(records)
        pause_count = 0
        total_pause_time = 0
        if records:
            for record in records:
                pause_count += 1
                if record.recovery_date_time:
                    total_pause_time += (record.recovery_date_time - record.risk_date_time).seconds
                else:
                    total_pause_time += 0
            CityMonthRecord.create_or_update(city, month, pause_count, total_pause_time)
            return True
        else:
            return False

    def report(self, parma):

        print(parma)
        record_id = parma.get('id')
        record = CityMonthRecord.get_record(record_id)
        tpl = DocxTemplate(TEMPLATE_DIR)
        total_pause_time = int(record.total_pause_time) / 60
        device_avarate = (1-(record.total_pause_time/(30 * 24 * 60 * 60))) * 100

        context = {
            'city': record.city.name,
            'year': datetime.strftime(datetime.now(), "%Y"),
            'month': record.month,
            'device_count': parma.get('device', None),
            'total_error': record.pause_count,
            'error_time': total_pause_time,
            'error_date': '',
            'device_avarate': device_avarate,
            'text': parma.get('markdown', None),
        }

        tpl.render(context)
        tpl.save(os.path.join(settings.DEVICE_REPORT_DIR, '{}_{}.docx'.format(record.month, record.city.name)))
        return True
