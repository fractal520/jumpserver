from django.shortcuts import render, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext as _
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.urls import reverse_lazy
from datetime import datetime
from .models.city import CityMonthRecord, City, CityPauseRecord
from .forms.dreportapp import CityUpdateForm, CityCreateForm, RecordUpdateForm
from common.permissions import AdminUserRequiredMixin
# Create your views here.


# 城市视图
class CityView(AdminUserRequiredMixin, ListView):
    model = City
    template_name = 'dreport/city_list.html'
    context_object_name = 'citys'


# 城市更新视图
class CityUpdateView(AdminUserRequiredMixin, UpdateView):
    model = City
    template_name = 'dreport/city_update.html'
    form_class = CityUpdateForm
    success_url = reverse_lazy('dreport:CityView')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Dreport'),
            'action': _('Update City'),
        }
        kwargs.update(context)
        print(self.request)
        return super().get_context_data(**kwargs)


# 城市创建视图
class CityCreateView(AdminUserRequiredMixin, CreateView):
    model = City
    template_name = 'dreport/city_update.html'
    form_class = CityCreateForm
    success_url = reverse_lazy('dreport:CityView')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Dreport'),
            'action': _('Create City'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


# 城市月度统计视图
class CityMonthView(AdminUserRequiredMixin, ListView):
    # model = CityMonthRecord
    template_name = 'dreport/city_month.html'
    context_object_name = 'city_month'

    def get_queryset(self):
        month = self.request.GET.get('month') if self.request.GET.get('month') else datetime.strftime(datetime.now(), '%m')
        queryset = CityMonthRecord.objects.filter(month=month)
        return queryset


# 全国熔断记录视图
class CityRecord(AdminUserRequiredMixin, ListView):
    model = CityPauseRecord
    template_name = 'dreport/city_record.html'
    context_object_name = 'records'
    ordering = '-risk_date_time'


class RecordUpdateView(AdminUserRequiredMixin, UpdateView):
    model = CityPauseRecord
    template_name = 'dreport/record_update.html'
    form_class = RecordUpdateForm
    success_url = reverse_lazy('dreport:CityRecord')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Dreport'),
            'action': _('Update Record'),
            'risk_time': self.request.GET.get
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
