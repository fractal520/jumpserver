from django.urls import path
from .. import views

app_name = 'devops'

urlpatterns = [
    path('index/', views.UserAssetListView.as_view(), name='index')
]
