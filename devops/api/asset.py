from rest_framework_bulk import BulkModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from assets import serializers
from assets.utils import LabelFilter
from common.mixins import IDInFilterMixin
from common.permissions import IsOrgAdminOrAppUser
from assets.models import Asset, Node, AdminUser


class AssetViewSet(IDInFilterMixin, LabelFilter, BulkModelViewSet):
    """
    API endpoint that allows Asset to be viewed or edited.
    """
    filter_fields = ("hostname", "ip")
    search_fields = filter_fields
    ordering_fields = ("hostname", "ip", "port", "comment")
    queryset = Asset.objects.all()
    serializer_class = serializers.AssetSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsOrgAdminOrAppUser,)

    def filter_node(self):
        node_id = self.request.query_params.get("node_id")
        if not node_id:
            return

        node = get_object_or_404(Node, id=node_id)
        show_current_asset = self.request.query_params.get("show_current_asset") in ('1', 'true')

        if node.is_root():
            if show_current_asset:
                self.queryset = self.queryset.filter(
                    Q(nodes=node_id) | Q(nodes__isnull=True)
                ).distinct()
            return
        if show_current_asset:
            self.queryset = self.queryset.filter(nodes=node).distinct()
        else:
            self.queryset = self.queryset.filter(
                nodes__key__regex='^{}(:[0-9]+)*$'.format(node.key),
            ).distinct()

    def filter_admin_user_id(self):
        admin_user_id = self.request.query_params.get('admin_user_id')
        if admin_user_id:
            admin_user = get_object_or_404(AdminUser, id=admin_user_id)
            self.queryset = self.queryset.filter(admin_user=admin_user)

    def get_queryset(self):
        self.queryset = super().get_queryset()\
            .prefetch_related('labels', 'nodes')\
            .select_related('admin_user')
        self.filter_admin_user_id()
        self.filter_node()
        return self.queryset.distinct()
