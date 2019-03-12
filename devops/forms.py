# ~*~ coding: utf-8 ~*~

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from orgs.mixins import OrgModelForm


class TaskForm(forms.ModelForm):
    class Meta:
        model = PlayBookTask
        fields = [
            'name', 'desc', 'ansible_role', 'run_as_admin', 'run_as', 'extra_vars', 'assets'
        ]
        help_texts = {
        }
        widgets = {
            'desc': forms.Textarea(),
            'assets': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('assets')
            }),
        }


class TaskUpdateForm(OrgModelForm):
    class Meta:
        model = PlayBookTask
        fields = ['name', 'desc', 'run_as_admin', 'extra_vars', 'assets']
        widgets = {
            'assets': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('assets')
            })
        }
        labels = {
            'name': '任务名称',
            'desc': '任务描述',
            'run_as_admin': '管理员身份运行',
            'extra_vars': '额外变量',
            'assets': '运行主机'
        }
        help_texts = {
            'extra_vars': '*变量格式为{key:value}格式,字符串需要用单引号括起来'
        }
