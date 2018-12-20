# -*- coding: utf-8 -*-
#

from rest_framework import generics
from common.permissions import IsOrgAdmin, IsOrgAdminOrAppUser
from ..models.city import City, CityMonthRecord
from ..utils import *
from django.http import JsonResponse


def create_month_record(request):
    print(request.POST)
    city_id = request.POST.get("id", None)
    date = request.POST.get("record-month", None)
    bot = MonthRecordFunction()
    bot.create(city_id=city_id, date=date)
    return JsonResponse(dict(code=200, msg=''))
