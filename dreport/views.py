from datetime import datetime

from django.utils.translation import ugettext as _
from django.views.generic import ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Q

from .models.city import CityMonthRecord, City, CityPauseRecord, CityWeekRecord
from .forms import CityUpdateForm, CityCreateForm, RecordUpdateForm, CityRecordCreateForm
from common.permissions import AdminUserRequiredMixin
from common.mixins import DatetimeSearchMixin
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
class CityRecord(AdminUserRequiredMixin, DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = CityPauseRecord
    template_name = 'dreport/city_record.html'
    context_object_name = 'records'
    ordering = '-risk_date_time'
    keyword = ''

    def get_queryset(self):
        self.queryset = CityPauseRecord.objects.all()
        self.keyword = self.request.GET.get('keyword', '')
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            self.queryset = self.queryset.order_by(*ordering)
            self.queryset = self.queryset.filter(
                risk_date_time__gt=self.date_from,
                risk_date_time__lt=self.date_to
            )
            if self.keyword:
                self.queryset = self.queryset.filter(
                    Q(city__name__icontains=self.keyword) | Q(remark__icontains=self.keyword)
                )
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('devops'),
            'action': _('Record list'),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'keyword': self.keyword,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


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
