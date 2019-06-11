from django.urls import path
from rest_framework import routers
from dbops import api


app_name = 'dbops'

router = routers.DefaultRouter()
#router.register('history', DeployHistoryViewSet, 'history')

urlpatterns = [
    path('check/', api.Check.as_view(), name='check'),
    path('exec/<pk>', api.Exec.as_view(), name='exec'),

]

urlpatterns += router.urls
