# ~*~ coding: utf-8 ~*~

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from orgs.mixins import OrgModelForm
from perms.utils import AssetPermissionUtil


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
        fields = ['name', 'desc', 'run_as_admin', 'extra_vars', 'assets', 'ansible_role', 'playbook_path']
        widgets = {
            'assets': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('assets')
            }),
            'ansible_role': forms.Select(attrs={
                'class': 'select2', 'data-placeholder': _('ansible_role')
            })
        }
        labels = {
            'name': '任务名称',
            'desc': '任务描述',
            'run_as_admin': '管理员身份运行',
            'extra_vars': '额外变量',
            'assets': '运行主机',
            'ansible_role': 'Ansible role',
            'playbook_path': 'Playbook路径'
        }
        help_texts = {
            'extra_vars': '*变量格式为{key:value}格式,字符串需要用单引号括起来',
            'ansible_role': '*更改role后必须重新设置playbookpath,如非必要请勿修改此项'
        }


class TaskUpdateAssetsForm(OrgModelForm):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        util = AssetPermissionUtil(request.user)
        _assets = util.get_assets_direct()
        al = [asset.id for asset in _assets.keys()]
        self.fields['assets'].queryset = self.fields['assets'].queryset.filter(id__in=al)

    class Meta:
        model = PlayBookTask
        fields = ['name', 'desc', 'extra_vars', 'assets']
        widgets = {
            'assets': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('assets')
            })
        }
        labels = {
            'name': '任务名称',
            'desc': '任务描述',
            'extra_vars': '额外变量',
            'assets': '运行主机',
        }


class AnsibleRoleUpdateForm(OrgModelForm):
    class Meta:
        model = AnsibleRole
        fields = ['name', 'desc']
        widgets = {}
        labels = {
            'name': 'AnsibleRole名称',
            'desc': 'Role详情及使用描述'
        }
        help_texts = {}
