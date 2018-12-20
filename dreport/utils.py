# -*- coding: utf-8 -*-
#

from .models.city import City, CityMonthRecord, CityPauseRecord
from django.core.exceptions import ObjectDoesNotExist


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
