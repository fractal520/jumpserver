from django.urls import path
from rest_framework import routers
from .. import api

app_name = 'devops'

router = routers.DefaultRouter()
router.register('tasks-opt', api.TaskOperationViewSet, 'task-opt')
router.register('roles', api.AnsibleRoleViewSet, 'role')
router.register('task', api.TaskViewSet, 'task')
router.register('history', api.TaskHistorySet, 'history')

urlpatterns = [
    path('assets/', api.UserGrantedAssetsApi.as_view(), name='my-assets'),
    path('supervisor/status/', api.GetSupervisorStatusApi.as_view(), name='supervisor-status'),
    path('supervisor/start_app/', api.StartAppApi.as_view(), name='start_app'),
    path('supervisor/stop_app/', api.StopAppApi.as_view(), name='stop_app'),
    path('supervisor/restart_app/', api.ReStartAppApi.as_view(), name='restart_app'),
    path('supervisor/get_log/', api.GetAPPLogApi.as_view(), name='get_log'),
    path('playbook/task-list/', api.PlayBookTaskListViewApi.as_view(), name='task-list'),
    path('tasks/<uuid:pk>/run/', api.TaskRun.as_view(), name='task-run'),
    path('tasks/<uuid:pk>/reset_playbook/', api.TaskResetPlayBook.as_view(), name='task-reset-playbook'),
    path('roles/zip/install/', api.InstallZipRoleView.as_view(), name='role-zip-install'),
    path('file_check_job/list/', api.CheckFileListAPIView.as_view(), name='file_check_list'),
    path('file_check_job/add/', api.CreateFileCheckJobAPIView.as_view(), name='file_check_add'),
    path('file_check_job/delete/<pk>', api.DeleteFileCheckJobAPIView.as_view(), name='file_check_delete'),
]

urlpatterns += router.urls
