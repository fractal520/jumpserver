from django.urls import path

from .. import views

app_name = 'deploy'


urlpatterns = [
    path('list/', views.DeployIndex.as_view(), name='deploy_list'),
    path('DeployOptionList/<uuid:pk>/', views.DeployOptionList.as_view(), name='DeployOptionList'),
    path('Deploy/<uuid:pk>/update/', views.DeployUpdateView.as_view(), name='deploy-update'),
    path('DeployRollback/<uuid:pk>/', views.DeployRollbackView.as_view(), name='DeployRollback'),
    path('AppStatus/<uuid:pk>/', views.AppStatusView.as_view(), name='AppStatus'),
]
