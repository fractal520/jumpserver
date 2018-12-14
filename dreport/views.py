from django.shortcuts import render, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from datetime import datetime
from .models.city import CityMonthRecord, City, CityPauseRecord
from common.permissions import AdminUserRequiredMixin
# Create your views here.


def index(request):
    print(request)
    return HttpResponse('hello,world!')


class CityView(AdminUserRequiredMixin, ListView):
    model = City
    template_name = 'dreport/city_list.html'
    context_object_name = 'citys'


class CityMonthView(AdminUserRequiredMixin, ListView):
    # model = CityMonthRecord
    template_name = 'dreport/city_month.html'
    context_object_name = 'city_month'

    def get_queryset(self):
        month = self.request.GET.get('month') if self.request.GET.get('month') else datetime.strftime(datetime.now(), '%m')
        queryset = CityMonthRecord.objects.filter(month=month)
        return queryset


class CityRecord(AdminUserRequiredMixin, ListView):
    model = CityPauseRecord
    template_name = 'dreport/city_record.html'
    context_object_name = 'records'
