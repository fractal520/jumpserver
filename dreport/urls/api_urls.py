from django.urls import path

from .. import api

app_name = 'dreport'

urlpatterns = [
    path('CityMonthView/batch_create/',
         api.batch_create_month_record, name='batch-create-month-record'),
    path('CityMonthView/create/',
         api.create_month_record, name='create-monthrecord'),
    path('CityMonthView/get_month_record/',
         api.get_month_record, name='get_month_record'),
    path('CityMonthView/make_report/',
         api.make_report, name='make_report'),
    path('CityMonthView/download_report/<uuid:pk>/',
         api.download_report, name='download_report'),
    path('CityRecord/download_record/',
         api.get_risk_record, name='get_risk_record'),
    path('CityRecord/download_record_from_time_quantum/',
         api.get_risk_record_from_time_quantum, name='get_risk_record_from_time_quantum'),
    path('CityWeekRecord/batch_create/',
         api.create_week_record, name='batch-create-week-record'),
    path('CityWeekRecord/get_week_record/',
         api.get_week_record, name='get_week_record'),
    path('CityWeekRecord/create_week_report/',
         api.create_week_report, name='create_week_report'),
    path('CityWeekRecord/download_week_report/<uuid:pk>/',
         api.download_week_report, name='download_week_report'),
]
