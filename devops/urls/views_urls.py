from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('devops_index/', views.index, name='devops_index'),
    path('/', views.AssetListView.as_view(), name='index')
]
