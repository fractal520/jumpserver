from django.shortcuts import render, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext as _
from django.views.generic import ListView, UpdateView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime
from .models.city import CityMonthRecord, City, CityPauseRecord, CityWeekRecord
from .forms import CityUpdateForm, CityCreateForm, RecordUpdateForm, CityRecordCreateForm
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
    ordering = '-risk_date_time'

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        d = timezone.datetime.now()
        if d.month == 1:
            # last_month = d.replace(year=d.year-1, month=12)
            pass
        else:
            # last_month = timezone.datetime.strftime(d.replace(month=d.month-1), "%Y-%m-%d")
            pass

        # queryset = CityPauseRecord.objects.filter(risk_date__gte=last_month)
        queryset = CityPauseRecord.objects.all()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset[0:150]


# 熔断记录更新视图
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

    def post(self, request, *args, **kwargs):
        self.object = None
        _mutable = request.POST._mutable
        request.POST._mutable = True
        # edit post start here
        recovery_date_time = request.POST.get('recovery_date_time', None)
        if recovery_date_time:
            recovery_date_time = datetime.strptime(request.POST.get('recovery_date_time'), "%Y/%m/%d %H:%M")
            request.POST['recovery_date'] = datetime.strftime(recovery_date_time, "%Y/%m/%d")
        request.POST._mutable = _mutable
        return super().post(request, *args, **kwargs)


# 熔断记录创建视图
class RecordCreateView(AdminUserRequiredMixin, CreateView):
    model = CityPauseRecord
    template_name = 'dreport/record_create.html'
    form_class = CityRecordCreateForm
    success_url = reverse_lazy('dreport:CityRecord')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Dreport'),
            'action': _('Create Record'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        _mutable = request.POST._mutable
        risk_date_time_edit = datetime.strptime(request.POST.get('risk_date_time'), "%Y/%m/%d %H:%M:%S")
        recovery_date_time = datetime.strptime(request.POST.get('recovery_date_time'), "%Y/%m/%d %H:%M:%S")
        request.POST._mutable = True
        request.POST['risk_date_time_edit'] = request.POST.get('risk_date_time')
        request.POST['risk_time'] = datetime.strftime(risk_date_time_edit, "%H:%M:%S")
        request.POST['risk_date'] = datetime.strftime(risk_date_time_edit, "%Y/%m/%d")
        request.POST['recovery_date'] = datetime.strftime(recovery_date_time, "%Y/%m/%d")
        request.POST._mutable = _mutable
        return super().post(request, *args, **kwargs)


class CityWeekView(AdminUserRequiredMixin, ListView):
    model = CityWeekRecord
    template_name = 'dreport/city_week.html'
    context_object_name = 'city_week'
