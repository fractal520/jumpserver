# -*- coding: utf-8 -*-
#

from ..utils import *
from django.http import JsonResponse, FileResponse
from ..models import CityMonthRecord


def create_month_record(request):
    print(request.POST)
    city_id = request.POST.get("id", None)
    date = request.POST.get("record-month", None)
    bot = MonthRecordFunction()
    if bot.create(city_id=city_id, date=date):
        return JsonResponse(dict(code=200, msg=''))
    else:
        return JsonResponse(dict(code=400, error=''))


def get_month_record(request):
    record_id = request.GET.get('id')
    data = {}
    if record_id:
        record = CityMonthRecord.get_record(record_id)
        data['city'] = record.city.name
        data['month'] = record.month
        data['total_error'] = record.pause_count
        data['error_time'] = record.total_pause_time
        return JsonResponse(dict(code=200, data=data))
    else:
        return JsonResponse(dict(code=400, error='no record'))


def make_report(request):
    parma = request.POST
    bot = MonthRecordFunction()
    bot.report(parma)
    return JsonResponse(dict(code=200, msg=''))


def download_report(request):
    parma = request.GET
    print(parma)
    # response = FileResponse(open(file_path, 'rb'))
    # response['Content-Type'] = 'application/octet-stream'
    # response['Content-Disposition'] = 'attachment;filename="example.tar.gz"'
    return JsonResponse(dict(code=200, msg=''))
