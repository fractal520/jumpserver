from django.urls import path, re_path
from rest_framework import routers
from dbops import api


app_name = 'dbops'

router = routers.DefaultRouter()
#router.register('history', DeployHistoryViewSet, 'history')

urlpatterns = [
    path('check/', api.Check.as_view(), name='check'),
    path('exec/<pk>', api.Exec.as_view(), name='exec'),
    path('rollback/<pk>', api.RollBack.as_view(), name='rollback'),
    path('audit/<work_id>', api.Audit.as_view(), name='audit'),
    #re_path(r'^audit/(?P<workid>\w+)/$', api.Audit.as_view(), name='audit'),

]

urlpatterns += router.urls
