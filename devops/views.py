from __future__ import unicode_literals

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy
from assets.models import *
from .forms import *
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
    success_url = reverse_lazy('deploy:deploy_list')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('Update Task'),
        }
        kwargs.update(context)
        return super(TaskUpdateView, self).get_context_data(**kwargs)
