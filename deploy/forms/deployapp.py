from django import forms
from django.utils.translation import gettext_lazy as _

from common.utils import get_logger
from orgs.mixins import OrgModelForm

from ..models import DeployList, DeployVersion


logger = get_logger(__file__)
__all__ = []


class AppUpdateForm(OrgModelForm):
    class Meta:
        model = DeployList
        fields = ['app_name', 'project', 'bound_asset', 'job_status']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'select2', 'data-placeholder': _('project')
            }),
            'bound_asset': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('bound_asset')
            }),
            'job_status': forms.Select(attrs={
                'class': 'select2', 'data-placeholder': _('job_status')
            }),
        }
        labels = {}
        help_texts = {
            'app_name': '* 千万不要随便修改',
        }
