from django.urls import path

from rest_framework import routers

from .. import views
from ..api import pushdeploy
from deploy.api import rollback, polling, GetBuildConsoleLogApiView, \
    DeployHistoryViewSet, ProjectListView, ProjectCreateView, ProjectDestroyView, ProjectUpdateView


app_name = 'deploy'

router = routers.DefaultRouter()
router.register('history', DeployHistoryViewSet, 'history')

urlpatterns = [
    path('get_jenkins_all/', views.get_jenkins_all, name='get_jenkins_all'),
    path('build_app/', views.build_app, name='build_app'),
    path('get_host_admin/', pushdeploy.get_host_admin, name='get_host_admin'),
    path('deploy_file_to_asset/', pushdeploy.deploy_file_to_asset, name='deploy_file_to_asset'),
    path('get_version_history/', pushdeploy.get_version_history, name='get_version_history'),
    path('rollback/', rollback, name='rollback'),
    path('polling/', polling, name='polling'),
    path('app/<uuid:pk>/console_log', GetBuildConsoleLogApiView.as_view(), name='console_log'),
    path('project/', ProjectListView.as_view(), name='project_list'),
    path('project/create/', ProjectCreateView.as_view(), name='project_create'),
    path('project/delete/<uuid:pk>', ProjectDestroyView.as_view(), name='project_delete'),
    path('project/update/<uuid:pk>', ProjectUpdateView.as_view(), name='project_update'),
]

urlpatterns += router.urls
