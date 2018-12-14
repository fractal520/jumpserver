from django.shortcuts import render, HttpResponse

# Create your views here.


def index(request):
    print(request)
    return HttpResponse('hello,world!')
