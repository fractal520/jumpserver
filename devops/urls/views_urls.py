from __future__ import unicode_literals
from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('app-form/', views.UserAssetListView.as_view(), name='app-form'),
    path('devops/play-task-list/', views.PlayBookListView.as_view(), name='play-task-list'),
    path('devops/play-task/create', views.TaskCreateView.as_view(), name='task-create'),
    path('devops/play-task/<uuid:pk>/update', views.TaskUpdateView.as_view(), name='task-update'),
    path('devops/play-task/<uuid:pk>/clone', views.TaskCloneView.as_view(), name='task-clone'),
    path('devops/play-task/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('devops/play-task/<uuid:pk>/history', views.TaskHistoryView.as_view(), name='task-history'),
    path('devops/play-task/<uuid:pk>/history-detail', views.TaskHistoryDetailView.as_view(), name='task-history-detail'),
    path('devops/ansible-role-list/', views.AnsibleRoleView.as_view(), name='ansible-role-list'),
    path('devops/ansible-role/<pk>/', views.AnsibleRoleDetailView.as_view(), name='role-detail'),
    path('devops/ansible-role/<pk>/update', views.AnsibleRoleUpdateView.as_view(), name='ansible-role-update'),
]
