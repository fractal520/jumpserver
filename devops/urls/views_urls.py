from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('index/', views.AssetListView.as_view(), name='index')
]
