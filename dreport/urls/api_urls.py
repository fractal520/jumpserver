from django.urls import path

from .. import api

app_name = 'dreport'

urlpatterns = [
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
]
