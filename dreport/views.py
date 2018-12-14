from django.shortcuts import render, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext as _
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.urls import reverse_lazy
from datetime import datetime
from .models.city import CityMonthRecord, City, CityPauseRecord
from .forms.dreportapp import AppUpdateForm
from common.permissions import AdminUserRequiredMixin
# Create your views here.


class CityView(AdminUserRequiredMixin, ListView):
    model = City
    template_name = 'dreport/city_list.html'
    context_object_name = 'citys'


class CityUpdateView(AdminUserRequiredMixin, UpdateView):
    model = City
    template_name = 'dereport/dereport_update.html'
    form_class = AppUpdateForm
    success_url = reverse_lazy('dreport:city_list')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Dreport'),
            'action': _('Update City'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


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
    ordering = '-create_time'
