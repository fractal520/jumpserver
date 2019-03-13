from __future__ import unicode_literals
from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('app-form/', views.UserAssetListView.as_view(), name='app-form'),
    path('play-task-list/', views.PlayBookListView.as_view(), name='play-task-list'),
    path('play-task/create', views.TaskCreateView.as_view(), name='task-create'),
    path('play-task/<uuid:pk>/update', views.TaskUpdateView.as_view(), name='task-update'),
    path('play-task/<uuid:pk>/clone', views.TaskCloneView.as_view(), name='task-clone'),
    path('play-task/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('play-task/<uuid:pk>/history', views.TaskHistoryView.as_view(), name='task-history'),
]
