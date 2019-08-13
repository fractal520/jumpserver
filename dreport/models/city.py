# -*- coding: utf-8 -*-
# author: niko
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
            logger.info('Month record update successful.')
        except ObjectDoesNotExist as error:
            logger.info(error, 'Month record will create by system.')
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

    RISK_LEVEL = (
        ("Alert", "影响交易"),
        ("Warning", "影响运营及可能影响交易"),
        ("Info", "其他")
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=False, verbose_name=_("City Name"))
    risk_date = models.DateField(null=True)
    recovery_date = models.DateField(null=True, blank=True)
    risk_date_time = models.DateTimeField(null=False)
    recovery_date_time = models.DateTimeField(null=True, blank=True, verbose_name="恢复时间")
    risk_date_time_edit = models.DateTimeField(null=True, blank=True, verbose_name="熔断时间")
    log_name = models.CharField(max_length=256, null=False, default='')
    remark = models.CharField(max_length=256, default='', blank=True, verbose_name="备注")
    risk_time = models.TimeField(null=True)
    risk_level = models.CharField(max_length=128, choices=RISK_LEVEL, null=True, blank=True, default=None, verbose_name="熔断记录等级")

    def __str__(self):
        return '{0}_{1}'.format(self.city.name, self.risk_date_time)

    @staticmethod
    def add_record(risk_list, risk_date):
        if risk_list:
            if CityPauseRecord.objects.filter(risk_date=risk_date):
                CityPauseRecord.objects.filter(risk_date=risk_date).delete()
                logger.info('{} risk record is already exist, system will delete it first.'.format(risk_date))
            for record in risk_list:
                record = record.split('\n')
                risk_time = record[0].split('.')[0]
                risk_date_time = risk_date+' '+risk_time
                try:
                    city = City.objects.get_or_create(name=record[1])[0]
                    logger.info('Get city {}.'.format(city.name))
                except ObjectDoesNotExist as error:
                    logger.info('city not exist, system will create it.')
                    City.objects.create(name=record[1])
                    city = City.objects.get(name=record[1])

                CityPauseRecord.objects.create(
                    city=city,
                    risk_date=risk_date,
                    risk_date_time=risk_date_time,
                    risk_date_time_edit=risk_date_time,
                    risk_time=risk_time
                )
                logger.info('Risk record {} create successful.'.format(record))
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
    select_year = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)

    def create_record(self, date, week, citys=City.objects.all()):
        print(date, week)
        logger.info("Add {} of {} record.".format(week, date.year))
        if date.weekday() == 6:
            end = date
            start = date + timedelta(days=-6)
        elif date.weekday() == 0:
            start = date
            end = date + timedelta(days=6)
        else:
            start = date - timedelta(days=date.weekday())
            end = date + timedelta(days=6-date.weekday())
        # print(start, end)
        for city in citys:
            records = CityPauseRecord.objects.filter(city=city, risk_date__gte=start, risk_date__lte=end)
            pause_count = 0
            total_pause_time = 0
            if records:
                for record in records:
                    if record.recovery_date_time:
                        pause_count += 1
                        total_pause_time += (record.recovery_date_time - record.risk_date_time).seconds
                    else:
                        total_pause_time += 0
                CityWeekRecord.objects.create(
                    city=city,
                    pause_count=pause_count,
                    total_pause_time=total_pause_time,
                    week_of_report=week,
                    select_date=date,
                    select_year=datetime.strftime(date, "%Y"),
                    start_date=start,
                    end_date=end
                )
                logger.info('City {} week record in {}week create successful.'.format(city.name, week))
            else:
                logger.info('City {} was no risk record in this {}week'.format(city.name, week))
                continue

        return True

    @classmethod
    def save_report(cls, record_id, filename):
        record = CityWeekRecord.objects.get(id=record_id)
        record.report_name = filename
        record.save()
        logger.info('Report name {} save in databases.'.format(filename))
        return True

    @classmethod
    def get_report(cls, record_id):
        record = CityWeekRecord.objects.get(id=record_id)
        logger.info('Get report {}.'.format(record.report_name))
        return record.report_name
