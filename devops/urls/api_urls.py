from django.urls import path
from rest_framework_nested import routers
from rest_framework_bulk.routes import BulkRouter
from .. import api

app_name = 'devops'
router = BulkRouter()
router.register(r'assets', api.AssetViewSet, 'asset')

urlpatterns = [

]
urlpatterns += router.urls
