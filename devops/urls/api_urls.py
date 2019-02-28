from django.urls import path
from rest_framework import routers
from .. import api

app_name = 'devops'

router = routers.DefaultRouter()
router.register(r'supervisor-status', api.GetSupervisorStatus, 'supervisor-status')


urlpatterns = [
    path('assets/', api.UserGrantedAssetsApi.as_view(), name='my-assets'),
]

urlpatterns += router.urls
