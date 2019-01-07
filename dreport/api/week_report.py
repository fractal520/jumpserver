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


def create_week_report(request):
    parm = request.POST
    if not parm.get('id', None):
        return JsonResponse(dict(code=400, error='记录获取失败'))
    record_id = parm.get('id')
    bot = WeekRecord()
    result = bot.report(record_id=record_id, parma=parm)
    return JsonResponse(dict(code=200, msg=result))


def get_week_record(request):
    record_id = request.GET.get('id')
    data = {}
    if record_id:
        record = CityWeekRecord.objects.get(id=record_id)
        data['city'] = record.city.name
        data['week_of_report'] = record.week_of_report
        data['total_error'] = record.pause_count
        data['error_time'] = record.total_pause_time
        return JsonResponse(dict(code=200, data=data))
    else:
        return JsonResponse(dict(code=400, error='no record'))


def download_week_report(request, pk):
    file = CityWeekRecord.get_report(pk)
    file_path = os.path.join(settings.DEVICE_REPORT_DIR, file)
    print(escape_uri_path(file_path))
    response = FileResponse(open(file_path, 'rb'))
    # response['Content-Type'] = 'application/octet-stream'
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file))
    return response
