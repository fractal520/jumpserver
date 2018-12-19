# -*- coding: utf-8 -*-
#
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from common.utils import get_logger
from datetime import datetime, timedelta

logger = get_logger('jumpserver')


# 城市表，记录城市名称和企业代码
class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=512)
    city_code = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


# 城市月份汇总表
class CityMonthRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, verbose_name=_("City Name"))
    month = models.IntegerField(null=False)
    pause_count = models.IntegerField(null=True, blank=True, default=0)
    total_pause_time = models.IntegerField(null=True, blank=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    edit_time = models.DateTimeField(auto_now=True)


# 城市熔断记录
class CityPauseRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, verbose_name=_("City Name"))
    risk_date = models.DateField(null=False, editable=False)
    recovery_date = models.DateField(null=True, blank=True)
    risk_date_time = models.DateTimeField(null=False, editable=False)
    recovery_date_time = models.DateTimeField(null=True, blank=True)
    risk_date_time_edit = models.DateTimeField(null=False, blank=True)
    log_name = models.CharField(max_length=256, null=False, default='')

    def add_record(self, risk_list, risk_date):
        print(risk_date)
        if risk_list:
            if CityPauseRecord.objects.filter(risk_date=risk_date):
                CityPauseRecord.objects.filter(risk_date=risk_date).delete()
            for record in risk_list:
                record = record.split('\n')
                risk_time = record[0].split('.')[0]
                risk_date_time = risk_date+' '+risk_time
                print(risk_date_time)
                try:
                    city = City.objects.get(name=record[1])
                    print('get city')
                except ObjectDoesNotExist as error:
                    City.objects.create(name=record[1])
                    city = City.objects.get(name=record[1])

                CityPauseRecord.objects.create(
                    city=city,
                    risk_date=risk_date,
                    risk_date_time=risk_date_time,
                    risk_date_time_edit=risk_date_time
                )
        else:
            return False
