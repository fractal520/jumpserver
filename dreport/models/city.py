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

    CORPORATION = "CORPORATION"
    SERVER = "SERVER"
    OTHER = "OTHER"

    TYPE_CHOICES = (
        (CORPORATION, CORPORATION),
        (SERVER, SERVER),
        (OTHER, OTHER)
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=512)
    city_code = models.IntegerField(null=True, blank=True)
    city_type = models.CharField(max_length=256, choices=TYPE_CHOICES, default="CORPORATION")

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
    year = models.IntegerField(null=False)
    report_name = models.CharField(max_length=512, null=True)

    @classmethod
    def get_report(cls, record_id):
        record = CityMonthRecord.objects.get(id=record_id)
        return record.report_name

    @classmethod
    def save_report(cls, record_id, filename):
        record = CityMonthRecord.objects.get(id=record_id)
        record.report_name = filename
        record.save()
        return True

    @classmethod
    def get_record(cls, record_id):
        return CityMonthRecord.objects.get(id=record_id)

    @classmethod
    def create_or_update(cls, city, month, pause_count, total_pause_time, year):
        try:
            record = CityMonthRecord.objects.get(city=city, month=month, year=year)
            record.pause_count = pause_count
            record.total_pause_time = total_pause_time
            record.save()
        except ObjectDoesNotExist as error:
            print(error, 'Record will create by system.')
            CityMonthRecord.objects.create(
                city=city,
                month=month,
                pause_count=pause_count,
                total_pause_time=total_pause_time,
                year=year
            )
            return True
        return True


# 城市熔断记录
class CityPauseRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=False, verbose_name=_("City Name"))
    risk_date = models.DateField(null=True)
    recovery_date = models.DateField(null=True, blank=True)
    risk_date_time = models.DateTimeField(null=False)
    recovery_date_time = models.DateTimeField(null=True, blank=True)
    risk_date_time_edit = models.DateTimeField(null=True, blank=True)
    log_name = models.CharField(max_length=256, null=False, default='')
    remark = models.CharField(max_length=256, default='', blank=True)
    risk_time = models.TimeField(null=True)

    def __str__(self):
        return '{0}_{1}'.format(self.city.name, self.risk_date_time)

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
                    risk_date_time_edit=risk_date_time,
                    risk_time=risk_time
                )
            return True
        else:
            return False


class CityWeekRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=False, verbose_name=_("City Name"))
    pause_count = models.IntegerField(null=True, blank=True, default=0)
    total_pause_time = models.IntegerField(null=True, blank=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    edit_time = models.DateTimeField(auto_now=True)
    report_name = models.CharField(max_length=512, null=True)
    week_of_report = models.IntegerField(null=False)
    select_date = models.DateField(null=False)
