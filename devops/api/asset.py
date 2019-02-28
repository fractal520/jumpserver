from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from assets.serializers import AssetGrantedSerializer
from users.models import User
from perms.utils import AssetPermissionUtil
from common.permissions import IsOrgAdminOrAppUser, IsValidUser
from orgs.utils import set_to_root_org


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


class GetSupervisorStatus(RetrieveAPIView):
    queryset = None
    serializer_class = None
    permission_classes = IsValidUser

    def retrieve(self, request, *args, **kwargs):
        result = [{"key": "supervisor", "value": "status"}]
        return Response(result, status=status.HTTP_200_OK)
