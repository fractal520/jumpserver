from django.urls import path

from .. import api

app_name = 'dreport'

urlpatterns = [
    path('CityMonthView/create/',
         api.create_month_record, name='create-monthrecord'),
    path('CityMonthView/get_month_record/',
         api.get_month_record, name='get_month_record'),
]
