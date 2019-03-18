from django.urls import path

from .. import views
from ..api import pushdeploy
from deploy.api import rollback, polling

app_name = 'deploy'

urlpatterns = [
    path('get_jenkins_all/', views.get_jenkins_all, name='get_jenkins_all'),
    path('build_app/', views.build_app, name='build_app'),
    path('get_host_admin/', pushdeploy.get_host_admin, name='get_host_admin'),
    path('deploy_file_to_asset/', pushdeploy.deploy_file_to_asset, name='deploy_file_to_asset'),
    path('get_version_history/', pushdeploy.get_version_history, name='get_version_history'),
    path('rollback/', rollback, name='rollback'),
    path('polling/', polling, name='polling'),
]
