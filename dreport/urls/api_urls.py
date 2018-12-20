from django.urls import path

from .. import api

app_name = 'dreport'

urlpatterns = [
        path('CityMonthView/create/',
             api.create_month_record, name='create-monthrecord'),
]
