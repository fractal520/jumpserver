from __future__ import unicode_literals
from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('devops/index/', views.DevOpsIndexView.as_view(), name='index'),
    path('app-form/', views.UserAssetListView.as_view(), name='app-form'),
    path('filecheck/', views.FileCheckListView.as_view(), name='filecheck'),
    path('filecheck/update/<pk>', views.FileCheckFormView.as_view(), name='filecheck-update'),
    path('ansible/play-task-list/', views.PlayBookListView.as_view(), name='play-task-list'),
    path('devops/play-task/create', views.TaskCreateView.as_view(), name='task-create'),
    path('devops/play-task/<uuid:pk>/update', views.TaskUpdateView.as_view(), name='task-update'),
    path('devops/play-task/<uuid:pk>/update_assets', views.TaskUpdateAssetsView.as_view(), name='task-update-assets'),
    path('devops/play-task/<uuid:pk>/clone', views.TaskCloneView.as_view(), name='task-clone'),
    path('devops/play-task/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('devops/play-task/<uuid:pk>/history', views.TaskHistoryView.as_view(), name='task-history'),
    path('devops/play-task/<uuid:pk>/history-detail', views.TaskHistoryDetailView.as_view(), name='task-history-detail'),
    path('devops/ansible-role-list/', views.AnsibleRoleView.as_view(), name='ansible-role-list'),
    path('devops/ansible-role/<pk>/', views.AnsibleRoleDetailView.as_view(), name='role-detail'),
    path('devops/ansible-role/<pk>/update', views.AnsibleRoleUpdateView.as_view(), name='ansible-role-update'),
    path('devops/routing-inspection-list/', views.RoutingInspectionListView.as_view(), name='routing-inspection-list'),
    path('celery/task/<uuid:pk>/log/', views.CustomCeleryTaskLogView.as_view(), name='celery-task-log'),
    # path('dashboard/fusion/', views.dashboard, name='dashboard'),
    path('dashboard/fusion/', views.ScssFusionDashboardView.as_view(), name='dashboard'),
]
