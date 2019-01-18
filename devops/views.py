from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def index(request):
    print('devops_index')
    return JsonResponse(dict(code=200, msg='devops index'))
