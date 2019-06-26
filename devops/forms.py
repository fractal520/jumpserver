# ~*~ coding: utf-8 ~*~

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from orgs.mixins import OrgModelForm
from perms.utils import AssetPermissionUtil
from assets.models import Asset


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


class FileCheckUpdateForm(forms.Form):

    city = forms.CharField(label="企业", empty_value="深圳", initial="深圳")

    node_type = forms.ChoiceField(label="节点类型", choices=(('ssh', 'ssh'), ('ftp', 'ftp')))
    way = forms.ChoiceField(label="渠道", choices=(('download', '下载'), ('upload', '上传')))
    asset = forms.ChoiceField(label="节点", widget=forms.widgets.Select(attrs={
                'class': 'select2', 'data-placeholder': _('asset')
            }))

    file_path = forms.CharField(label="文件路径")
    file_format = forms.CharField(label="文件格式")
    time_format = forms.CharField(label="时间格式")

    trigger = forms.ChoiceField(label="触发器", choices=(('', '----'), ('interval', '循环任务'), ('cron', '定时任务')))
    time_delta = forms.ChoiceField(label="文件日期时间差", choices=(
        (-2, '两天前'), (-1, '一天前'), (0, '当天'), (1, '一天后'), (2, '两天后')
    ))

    def __init__(self, request, *args, **kwargs):
        self.job_data = kwargs.pop('job_data')
        super(FileCheckUpdateForm, self).__init__(*args, **kwargs)
        self.user = request.user

        self.fields['city'].initial = self.job_data.get('city')

        self.fields['node_type'].initial = self.job_data.get('node_type')
        self.fields['way'].initial = self.job_data.get('way')
        self.fields['asset'].choices = self._asset_choice()
        self.fields['asset'].initial = self.job_data.get('asset_id')

        self.fields['file_path'].initial = self.job_data.get('file_path')
        self.fields['file_format'].initial = self.job_data.get('file_format')
        self.fields['time_format'].initial = self.job_data.get('time_format')

        self.fields['trigger'].initial = self.job_data.get('trigger')
        self.fields['time_delta'].initial = self.job_data.get('time_delta')

    def _asset_choice(self):
        util = AssetPermissionUtil(self.user)
        _assets = util.get_assets()
        choice = [('', '----')]
        for asset in _assets.keys():
            choice = choice + [(str(asset.id), "{}({})".format(asset.ip, asset.hostname))]
        return choice
