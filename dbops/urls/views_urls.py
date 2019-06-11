from django.urls import path

from .. import views

app_name = 'dbops'


urlpatterns = [
    path('dbs/', views.Dbs.as_view(), name='dbs'),
    path('sqlordercreate/', views.SqlOrderCreate.as_view(), name='sqlordercreate'),
    path('sqlorderlist/', views.SqlOrderList.as_view(), name='sqlorderlist'),
    path('sqlexeclist/', views.SqlExecList.as_view(), name='sqlexeclist'),
    path(r'^sqlexecdetail/(?P<pk>[0-9]+)/$', views.SqlExecDetail.as_view(), name='sqlexecdetail'),
]
