from django.urls import path, re_path

from .. import views

app_name = 'dbops'


urlpatterns = [
    path('dbinfos/', views.DbInfos.as_view(), name='dbinfos'),
    path('sqlordercreate/', views.SqlOrderCreate.as_view(), name='sqlordercreate'),
    path('sqlorderlist/', views.SqlOrderList.as_view(), name='sqlorderlist'),
    path('sqlexeclist/', views.SqlExecList.as_view(), name='sqlexeclist'),
    re_path(r'^sqlexecdetail/(?P<pk>[0-9]+)/$', views.SqlExecDetail.as_view(), name='sqlexecdetail'),
]
