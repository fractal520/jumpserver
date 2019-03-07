from django.urls import path
from rest_framework import routers
from .. import api

app_name = 'devops'

router = routers.DefaultRouter()
router.register('tasks-opt', api.TaskOperationViewSet, 'task-opt')
router.register('roles', api.AnsibleRoleViewSet, 'role')

urlpatterns = [
    path('assets/', api.UserGrantedAssetsApi.as_view(), name='my-assets'),
    path('supervisor/status/', api.GetSupervisorStatusApi.as_view(), name='supervisor-status'),
    path('supervisor/start_app/', api.StartAppApi.as_view(), name='start_app'),
    path('supervisor/stop_app/', api.StopAppApi.as_view(), name='stop_app'),
    path('supervisor/restart_app/', api.ReStartAppApi.as_view(), name='restart_app'),
    path('playbook/task-list/', api.PlayBookTaskListViewApi.as_view(), name='task-list'),
]

urlpatterns += router.urls
