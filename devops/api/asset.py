from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from assets.serializers import AssetGrantedSerializer
from assets.models import Asset
from users.models import User
from deploy.models import DeployList
from perms.utils import AssetPermissionUtil
from common.permissions import IsOrgAdminOrAppUser, IsValidUser
from orgs.utils import set_to_root_org
from devops.api.cesi import CesiAPI


class UserGrantedAssetsApi(ListAPIView):
    """
    用户授权的所有资产
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    serializer_class = AssetGrantedSerializer

    def change_org_if_need(self):
        if self.request.user.is_superuser or \
                self.request.user.is_app or \
                self.kwargs.get('pk') is None:
            set_to_root_org()

    def get_queryset(self):
        self.change_org_if_need()
        user_id = self.kwargs.get('pk', '')
        queryset = []

        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = self.request.user

        util = AssetPermissionUtil(user)
        for k, v in util.get_assets().items():
            system_users_granted = [s for s in v if s.protocol == k.protocol]
            k.system_users_granted = system_users_granted
            queryset.append(k)
        return queryset

    def get_permissions(self):
        if self.kwargs.get('pk') is None:
            self.permission_classes = (IsValidUser,)
        return super().get_permissions()


class GetSupervisorStatusApi(RetrieveAPIView):
    """
    获取对应资产的应用情况
    """
    queryset = DeployList.objects.all()
    permission_classes = (IsValidUser,)

    def retrieve(self, request, *args, **kwargs):
        app_id = request.GET.get('app_id')
        host_id = request.GET.get('host_id')
        app = DeployList.objects.get(id=app_id)
        asset = Asset.objects.get(id=host_id)
        cesi = CesiAPI()
        cesi.login()
        result = cesi.get_process(node_name=asset.hostname, process_name=app.app_name)
        if not result[0]:
            return Response({'code': 400, 'error': result[1]})

        data = eval(result, {'true': 0, 'false': 1})
        uptime = data['process']['uptime']
        if ':' in uptime:
            uptime += ' hours'
        else:
            uptime += ' days'

        data = {
            'code': 200,
            'pid': data['process']['pid'],
            'uptime': uptime,
            'status': data['process']['statename']
        }
        return Response(data)
