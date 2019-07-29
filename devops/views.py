from __future__ import unicode_literals

import json
import requests as Requests

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, CreateView, UpdateView, RedirectView, DetailView, FormView
from django.urls import reverse_lazy
from django.conf import settings

from assets.models import *
from assets.views import UserAssetListView as UAL
from common.permissions import SuperUserRequiredMixin, IsValidUser
from common.utils import get_logger
from .forms import *
from devops.models import PlayBookTask, TaskHistory
from ops.views import TaskListView, CeleryTaskLogView
from ops.models import CeleryTask
# Create your views here.

logger = get_logger('jumpserver')


class DevOpsIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/devops_index.html'

    def get_context_data(self, **kwargs):
        context = {
            'action': _('任务中心'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class UserAssetListView(UAL):
    template_name = 'devops/user_asset_list.html'


class PlayBookListView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/play_task_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('Playbook任务列表'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = PlayBookTask
    template_name = 'devops/task_create.html'
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('Create Task'),
        }
        kwargs.update(context)
        return super(TaskCreateView, self).get_context_data(**kwargs)


class TaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = PlayBookTask
    template_name = 'devops/task_update.html'
    form_class = TaskUpdateForm
    success_url = reverse_lazy('devops:play-task-list')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('Update Task'),
        }
        kwargs.update(context)
        return super(TaskUpdateView, self).get_context_data(**kwargs)


class TaskUpdateAssetsView(TaskUpdateView):
    template_name = 'devops/task_update_assets.html'
    form_class = TaskUpdateAssetsForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request, **self.get_form_kwargs())


class TaskCloneView(SuperUserRequiredMixin, RedirectView):
    url = reverse_lazy('devops:play-task-list')

    def get(self, request, *args, **kwargs):
        #: 克隆一个变量组
        old_task = PlayBookTask.objects.get(id=kwargs['pk'])
        new_task = PlayBookTask(name=old_task.name + "-copy-" + uuid.uuid4().hex[0:8], desc=old_task.desc + "-copy",
                                ansible_role_id=old_task.ansible_role_id)
        new_task.save()
        new_task.create_playbook(new_task.ansible_role)
        return super(TaskCloneView, self).get(request, *args, **kwargs)


class TaskDetailView(IsValidUser, DetailView):
    model = PlayBookTask
    template_name = 'devops/task_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('devops'),
            'action': _('Play task detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class TaskHistoryView(IsValidUser, DetailView):
    model = PlayBookTask
    template_name = 'devops/task_history.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('devops'),
            'action': _('Task run history'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class TaskHistoryDetailView(IsValidUser, DetailView):
    model = TaskHistory
    template_name = 'devops/task_history_detail.html'

    def get_context_data(self, **kwargs):

        hitory = self.get_object()
        history_info = [line for line in hitory.result_info.split('\n')]
        context = {
            'app': _('devops'),
            'action': _('Task history detail'),
            'history_info': history_info,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AnsibleRoleView(IsValidUser, TemplateView):
    template_name = 'devops/ansible_role_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('devops'),
            'action': _('Ansible role list'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AnsibleRoleUpdateView(IsValidUser, SuccessMessageMixin, UpdateView):
    model = AnsibleRole
    template_name = 'devops/role_update.html'
    form_class = AnsibleRoleUpdateForm
    success_url = reverse_lazy('devops:ansible-role-list')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('Update Task'),
        }
        kwargs.update(context)
        return super(AnsibleRoleUpdateView, self).get_context_data(**kwargs)


class AnsibleRoleDetailView(IsValidUser, DetailView):
    model = AnsibleRole
    template_name = 'devops/role_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('devops'),
            'action': _('Role detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class FileCheckListView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/file_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'action': _('对账文件检查状态'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class FileCheckFormView(IsValidUser, FormView):
    template_name = 'devops/file_list_update.html'
    form_class = FileCheckUpdateForm
    success_url = reverse_lazy('devops:filecheck')

    def get_job_detail(self, job_id):
        url = "http://{}/api/job/detail/{}".format(settings.RDM_URL, job_id)
        response = Requests.get(url=url)
        data = response.json()
        return data.get('data')

    def update_job(self, data):
        job_id = self.request.get_full_path_info().split('/')[-1]
        url = "http://{}/api/update/job/{}".format(settings.RDM_URL, job_id)
        node = Asset.objects.filter(id=data.pop('asset')).first()
        data['node_ip'] = node.ip
        data['asset_id'] = str(node.id)
        try:
            response = Requests.post(url=url, json=json.dumps(data))
            logger.info(response.text)
            return response
        except BaseException as e:
            logger.error(str(e))
            return False

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(FileCheckFormView, self).get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        kwargs = super(FileCheckFormView, self).get_form_kwargs()
        data = self.request
        job_id = data.get_full_path_info().split('/')[-1]
        kwargs.update({
            'job_data': self.get_job_detail(job_id),
        })
        return kwargs

    def form_valid(self, form):
        if self.update_job(form.cleaned_data):
            return super(FileCheckFormView, self).form_valid(form)


class RoutingInspectionListView(TaskListView):

    def get_queryset(self):
        return super(RoutingInspectionListView, self).get_queryset().filter(name__icontains="Daily routing inspection")


class CustomCeleryTaskLogView(CeleryTaskLogView):
    permission_classes = [IsValidUser]
