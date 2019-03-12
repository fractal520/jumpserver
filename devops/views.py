from __future__ import unicode_literals

import logging
import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, CreateView, UpdateView, RedirectView, DetailView
from django.urls import reverse_lazy
from assets.models import *
from common.permissions import SuperUserRequiredMixin
from .forms import *
from devops.models import PlayBookTask, TaskHistory
# Create your views here.

logger = logging.getLogger(__name__)


class UserAssetListView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/user_asset_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'action': _('My assets'),
            'system_users': SystemUser.objects.all(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class PlayBookListView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/play_task_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('My Play'),
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


class TaskCloneView(SuperUserRequiredMixin, RedirectView):
    url = reverse_lazy('devops:play-task-list')

    def get(self, request, *args, **kwargs):
        #: 克隆一个变量组
        old_task = PlayBookTask.objects.get(id=kwargs['pk'])
        new_task = PlayBookTask(name=old_task.name + "-copy-" + uuid.uuid4().hex, desc=old_task.desc + "-copy",
                                ansible_role_id=old_task.ansible_role_id)
        new_task.save()
        new_task.create_playbook(new_task.ansible_role)
        return super(TaskCloneView, self).get(request, *args, **kwargs)


class TaskDetailView(SuperUserRequiredMixin, DetailView):
    model = PlayBookTask
    template_name = 'devops/task_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('devops'),
            'action': _('Play task detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class TaskHistoryView(SuperUserRequiredMixin, DetailView):
    model = PlayBookTask
    template_name = 'devops/task_history.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Task run history'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
