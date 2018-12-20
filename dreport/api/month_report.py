# -*- coding: utf-8 -*-
#

from rest_framework import generics
from common.permissions import IsOrgAdmin, IsOrgAdminOrAppUser
from ..models.city import City, CityMonthRecord
from django.http import JsonResponse


def create_month_record(request):
    data = request.POST
    print(data)
    return JsonResponse(dict(code=200, msg=''))
