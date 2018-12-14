# -*- coding: utf-8 -*-
#
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from common.utils import get_logger

logger = get_logger('jumpserver')


# 城市表，记录城市名称和企业代码
class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=512)
    city_code = models.IntegerField(blank=True)

    def __str__(self):
        return self.name


class CityMonthRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, verbose_name=_("City Name"))
    month = models.IntegerField(null=False)
    pause_count = models.IntegerField(blank=True, default=0)
    total_pause_time = models.IntegerField(blank=True, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    edit_time = models.DateTimeField(auto_now=True)


class CityPauseRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, verbose_name=_("City Name"))
    risk_date = models.DateField(null=False, editable=False)
    recovery_date = models.DateField(blank=True)
    risk_date_time = models.DateTimeField(null=False, editable=False)
    recovery_date_time = models.DateTimeField(blank=True)
