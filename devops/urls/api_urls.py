from django.urls import path
from .. import api

app_name = 'devops'


urlpatterns = [
    path('assets/', api.UserGrantedAssetsApi.as_view(), name='my-assets'),
    path('supervisor/status/', api.GetSupervisorStatusApi.as_view(), name='supervisor-status'),
    path('supervisor/start_app/', api.StartAppApi.as_view(), name='start_app'),
    path('supervisor/stop_app/', api.StopAppApi.as_view(), name='stop_app'),
    path('supervisor/restart_app/', api.ReStartAppApi.as_view(), name='restart_app'),
]
