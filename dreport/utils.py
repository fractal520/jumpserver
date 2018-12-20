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
        return True
