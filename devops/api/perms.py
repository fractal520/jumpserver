from django.db.models import Q

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (
    ListAPIView, get_object_or_404
)

from assets.models import Asset
from perms.api.mixin import UserPermissionCacheMixin, GrantAssetsMixin
from common.permissions import IsValidUser, IsOrgAdminOrAppUser
from perms.hands import User
from perms.utils import (
    AssetPermissionUtil,
)
from devops.serializers import CustomAssetGrantedSerializer


class CustomGrantAssetsMixin(GrantAssetsMixin):
    serializer_class = CustomAssetGrantedSerializer

    def search_queryset(self, assets_items):
        search = self.request.query_params.get("search")
        if not search:
            return assets_items
        assets_map = {asset['id']: asset for asset in assets_items}
        assets_ids = set(assets_map.keys())
        # 重写资产搜索条件筛选
        assets_ids_search = Asset.objects.filter(id__in=assets_ids).filter(
            Q(hostname__icontains=search) | Q(ip__icontains=search) | Q(comment__icontains=search)
        ).values_list('id', flat=True)
        return [assets_map.get(asset_id) for asset_id in assets_ids_search]


class UserGrantedAssetsApi(UserPermissionCacheMixin, CustomGrantAssetsMixin, ListAPIView):
    """
    用户授权的所有资产
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        user_id = self.kwargs.get('pk', '')
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = self.request.user
        return user

    def get_queryset(self):
        user = self.get_object()
        util = AssetPermissionUtil(user, cache_policy=self.cache_policy)
        queryset = util.get_assets()
        return queryset

    def get_permissions(self):
        if self.kwargs.get('pk') is None:
            self.permission_classes = (IsValidUser,)
        return super().get_permissions()
