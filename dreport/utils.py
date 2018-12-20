# -*- coding: utf-8 -*-
#

from .models.city import City, CityMonthRecord, CityPauseRecord
from django.core.exceptions import ObjectDoesNotExist


class MonthRecordFunction(object):

    def create(self, city_id, date):
        try:
            city = City.objects.get(id=city_id[0])
        except ObjectDoesNotExist as error:
            print(error)
            return False
        print(date)
        # CityPauseRecord.objects.filter(risk_date__month=12, risk_date__year=2018)
        return True
