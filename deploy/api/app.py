# encoding: utf-8

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from deploy.models import DeployList
from common.permissions import IsValidUser


class GetBuildConsoleLogApiView(RetrieveAPIView):

    queryset = DeployList.objects.all()
    permission_classes = (IsValidUser,)

    def retrieve(self, request, *args, **kwargs):
        app = self.get_object()
        console_log = app.build_console_output
        console_log = console_log.replace('\r', '\n')
        console_log = console_log.split('\n')

        return Response(dict(code=200, message=console_log))
