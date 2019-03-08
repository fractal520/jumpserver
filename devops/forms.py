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
        fields = ['name', 'desc', 'ansible_role', 'run_as_admin', 'run_as', 'extra_vars', 'assets']
        widgets = {
            'assets': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('assets')
            }),
            'ansible_role': forms.Select(attrs={
                'class': 'select2', 'data-placeholder': _('ansible_role')
            })
        }
        labels = {}
        help_texts = {
            'ansible_role': '* 不要随便修改',
        }
