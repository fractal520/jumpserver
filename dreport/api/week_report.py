# -*- coding: utf-8 -*-
#

from ..utils import *
from django.http import JsonResponse, FileResponse
from ..models import CityWeekRecord, City
from django.conf import settings
from django.utils.encoding import escape_uri_path
from django.utils import timezone
from datetime import datetime


def create_week_record(request):
    parm = request.POST
    if not parm.get('record-week', None):
        return JsonResponse(dict(code=400, error='日期错误'))
    date = datetime.strptime(parm.get('record-week'), "%Y-%m-%d")
    week = date.strftime("%W")
    bot = WeekRecord()
    if parm.get('city', None):
        city = City.objects.filter(name=parm.get('city'))
        bot.create(date=date, week=week, city=city)
        return JsonResponse(dict(code=200, msg=""))
    bot.create(date=date, week=week, city=None)
    return JsonResponse(dict(code=200, msg=""))
