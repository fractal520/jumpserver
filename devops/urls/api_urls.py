from django.urls import path
from .. import api

app_name = 'devops'


urlpatterns = [
    path('assets/', api.UserGrantedAssetsApi.as_view(),
         name='my-assets')
]
