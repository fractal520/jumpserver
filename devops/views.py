from __future__ import unicode_literals

import logging

from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from assets.models import *
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
