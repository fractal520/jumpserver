# -*- coding: utf-8 -*-
#

from rest_framework import generics
from common.permissions import IsOrgAdmin, IsOrgAdminOrAppUser
from ..models.city import City, CityMonthRecord
from django.http import JsonResponse


@IsOrgAdmin
def create_month_record(request):
    print(request)
    return JsonResponse(dict(code=200))
