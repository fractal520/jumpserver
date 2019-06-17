from django.shortcuts import render
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from django.views.generic import ListView, CreateView,DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from apps.common.utils import get_logger
from .models.dbinfo import DbInfo
from .models.sqlinfo import SqlOrder, SqlRecord
from .forms.sqlorder import SqlUpdateForm

# Create your views here.

logger = get_logger('jumpserver')


class Dbs(LoginRequiredMixin, ListView):
    model = DbInfo
    template_name = 'dbops/dbinfos.html'
    context_object_name = 'dbs'


class SqlOrderCreate(LoginRequiredMixin, CreateView):
    model = SqlOrder
    form_class = SqlUpdateForm
    template_name = 'dbops/sqlordercreate.html'
    success_url = reverse_lazy('dbops:sqlorderlist')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs


class SqlOrderList(LoginRequiredMixin, ListView):
    model = SqlOrder
    template_name = 'dbops/sqlorderlist.html'
    context_object_name = 'sqlorders'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('insert_date').reverse()


class SqlExecList(LoginRequiredMixin, ListView):
    model = SqlOrder
    template_name = 'dbops/sqlexeclist.html'
    context_object_name = 'sqlexecs'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(Q(status=4) | Q(status=3)).order_by('insert_date').reverse()


class SqlExecDetail(LoginRequiredMixin, ListView):
    model = SqlRecord
    template_name = 'dbops/sqlexecdetail.html'
    context_object_name = 'sqlrecords'

    def get_queryset(self):
        qs = super().get_queryset()
        work_id = self.kwargs.get('pk')
        return qs.filter(work_id=work_id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'work_id': self.kwargs.get('pk')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
