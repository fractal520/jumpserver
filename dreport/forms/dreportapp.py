# encoding: utf-8
from django import forms
from django.utils.translation import gettext_lazy as _

from common.utils import get_logger
from orgs.mixins import OrgModelForm

from ..models.city import City, CityPauseRecord


logger = get_logger(__file__)
__all__ = ['CityUpdateForm', 'CityCreateForm', 'RecordUpdateForm', 'CityRecordCreateForm']


class CityUpdateForm(OrgModelForm):
    class Meta:
        model = City
        fields = ['name', 'city_code']
        labels = {}
        help_texts = {
            'name': '* 请输入规范的城市名',
            'city_code': '* 请输入对应的企业码'
        }


class CityCreateForm(OrgModelForm):
    class Meta:
        model = City
        fields = ['name', 'city_code']
        labels = {}
        help_texts = {
            'name': '* 请输入规范的城市名',
            'city_code': '* 请输入对应的企业码'
        }


class RecordUpdateForm(OrgModelForm):
    class Meta:
        model = CityPauseRecord
        fields = ['recovery_date_time', 'remark']
        labels = {}
        help_texts = {
            'recovery_date_time': '* 请输入熔断恢复时间',
            'remark': '在此请输入备注'
        }


class CityRecordCreateForm(OrgModelForm):
    class Meta:
        model = CityPauseRecord
        fields = [
            'city',
            'risk_date_time',
            'risk_date_time_edit',
            'risk_time',
            'risk_date',
            'recovery_date_time',
            'recovery_date',
            'remark'
        ]
        labels = {}
        help_texts = {
            'city': '* 请输入规范的城市名',
            'risk_date_time': '* 请输入规范的日期格式 YYYY-mm-dd HH:MM:SS',
            'recovery_date_time': '*请输入规范的日期格式 YYYY-mm-dd HH:MM:SS',
            'remark': '请输入备注'
        }
