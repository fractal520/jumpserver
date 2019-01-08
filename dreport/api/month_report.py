# -*- coding: utf-8 -*-
#

from ..utils import *
from django.http import JsonResponse, FileResponse
from ..models import CityMonthRecord
from django.conf import settings
from django.utils.encoding import escape_uri_path


def create_month_record(request):
    city_id = request.POST.get("id", None)
    date = request.POST.get("record-month", None)
    bot = MonthRecordFunction()
    logger.info('API create {} {} record.'.format(city_id, date))
    if bot.create(city_id=city_id, date=date):
        return JsonResponse(dict(code=200, msg=''))
    else:
        return JsonResponse(dict(code=400, error='该城市{}没有熔断记录'.format(date)))


def batch_create_month_record(request):
    if not request.POST.get("record-month", None):
        return JsonResponse(dict(code=400, error='请选择时间'))
    date = request.POST.get("record-month", None)
    bot = MonthRecordFunction()
    result, msg = bot.batch_create(date=date)
    logger.info('API batch create month record {}.'.format(msg))
    if result:
        return JsonResponse(dict(code=200, msg=msg))
    else:
        return JsonResponse(dict(code=400, error=msg))


def get_month_record(request):
    record_id = request.GET.get('id')
    data = {}
    if record_id:
        logger.info('API get month record {}.'.format(record_id))
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
    if not bot.report(parma):
        return JsonResponse(dict(code=400, error='没有记录'))
    logger.info('API create month report.')
    return JsonResponse(dict(code=200, msg=''))


def download_report(request, pk):
    file = CityMonthRecord.get_report(pk)
    file_path = os.path.join(settings.DEVICE_REPORT_DIR, file)
    response = FileResponse(open(file_path, 'rb'))
    # response['Content-Type'] = 'application/octet-stream'
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file))
    logger.info('Download file {}.'.format(file))
    return response


def get_risk_record(request):
    if not request.GET.get('record-month'):
        return JsonResponse(dict(code=400, error='请选择日期'))
    bot = RiskRecord()
    file = bot.create(request.GET.get('record-month'))
    file_path = os.path.join(settings.DEVICE_REPORT_DIR, file)
    response = FileResponse(open(file_path, 'rb'))
    # response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file))
    logger.info('Download file {}.'.format(file))
    return response


def get_risk_record_from_time_quantum(request):
    if not request.GET.get('start-date') or not request.GET.get('end-date'):
        return JsonResponse(dict(code=400, error='请选择日期'))
    bot = RiskRecord()
    file = bot.create(request.GET, time_quantum=True)
    file_path = os.path.join(settings.DEVICE_REPORT_DIR, file)
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file))
    logger.info('Download file {}.'.format(file))
    return response

