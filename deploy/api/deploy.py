# encoding: utf-8

from rest_framework import viewsets

from deploy.models import DeployRecord, DeployList
from deploy.serializers import DeployHistorySerializer
from common.permissions import IsValidUser


class DeployHistoryViewSet(IsValidUser, viewsets.ModelViewSet):
    queryset = DeployRecord.objects.all()
    serializer_class = DeployHistorySerializer
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        app_id = self.request.query_params.get('app')
        if app_id:
            app = DeployList.objects.filter(id=app_id)
            self.queryset = self.queryset.filter(app_name__in=app).order_by("-deploy_time")

        return self.queryset
