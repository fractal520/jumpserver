from django.shortcuts import render, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext as _
from django.views.generic import ListView, UpdateView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
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
            'action': _('Update City')
        }
        kwargs.update(context)
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
    model = CityMonthRecord
    template_name = 'dreport/city_month.html'
    context_object_name = 'city_month'


# 全国熔断记录视图
class CityRecord(AdminUserRequiredMixin, ListView):
    model = CityPauseRecord
    template_name = 'dreport/city_record.html'
    context_object_name = 'records'
    ordering = '-risk_date'

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        d = timezone.datetime.now()
        if d.month == 1:
            last_month = d.replace(year=d.year-1, month=12)
        else:
            last_month = timezone.datetime.strftime(d.replace(month=d.month-1), "%Y-%m-%d")

        queryset = CityPauseRecord.objects.filter(risk_date__gte=last_month)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


class RecordUpdateView(AdminUserRequiredMixin, UpdateView):
    model = CityPauseRecord
    template_name = 'dreport/record_update.html'
    form_class = RecordUpdateForm
    success_url = reverse_lazy('dreport:CityRecord')
    context_object_name = 'record'

    def get_context_data(self, **kwargs):
        path = self.request.path
        record_id = path.split('/')[-3]
        try:
            record = CityPauseRecord.objects.get(id=record_id)
        except ObjectDoesNotExist as error:
            record = None
            print(error)
        context = {
            'app': _('Dreport'),
            'action': _('Update Record'),
            'risk_time': record.risk_date_time,
            'city_name': record.city.name
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
