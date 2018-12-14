# encoding: utf-8
from django import forms
from django.utils.translation import gettext_lazy as _

from common.utils import get_logger
from orgs.mixins import OrgModelForm

from ..models.city import City


logger = get_logger(__file__)
__all__ = []


class AppUpdateForm(OrgModelForm):
    class Meta:
        model = City
        fields = ['name', 'city_code']
        labels = {}
        help_texts = {
            'name': '* 请输入规范的城市名',
            'city_code': '* 请输入对应的企业码'
        }
