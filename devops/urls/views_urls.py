from __future__ import unicode_literals
from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('index/', views.UserAssetListView.as_view(), name='index'),
    path('play-task-list/', views.PlayBookListView.as_view(), name='play-task-list'),
    path('play-task/create', views.TaskCreateView.as_view(), name='task-create'),
    path('play-task/<uuid:pk>/update', views.TaskUpdateView.as_view(), name='task-update'),
]
