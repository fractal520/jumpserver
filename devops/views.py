from __future__ import unicode_literals

import logging

from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
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


class TaskCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/task_create.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Devops'),
            'action': _('Create Task'),
            'form': TaskForm,
        }
        kwargs.update(context)
        return super(TaskCreateView, self).get_context_data(**kwargs)