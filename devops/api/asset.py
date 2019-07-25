from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from assets.serializers import AssetSerializer
from assets.models import Asset
from users.models import User
from deploy.models import DeployList
from perms.utils import AssetPermissionUtil
from common.permissions import IsOrgAdminOrAppUser, IsValidUser
from orgs.utils import set_to_root_org
from devops.api.cesi import CesiAPI
from  devops.utils import translate_timestamp
from common.utils import get_logger
from assets.api import AssetViewSet

logger = get_logger('jumpserver')


class UserGrantedAssetsApi(ListAPIView):
    """
    用户授权的所有资产
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    serializer_class = AssetSerializer

    def change_org_if_need(self):
        if self.request.user.is_superuser or \
                self.request.user.is_app or \
                self.kwargs.get('pk') is None:
            set_to_root_org()

    def get_queryset(self):
        term = self.request.GET.get('term', None)
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
            if term:
                if term in k.hostname or term in k.ip:
                    queryset.append(k)
            else:
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
        # cesi.login()
        result = cesi.get_process(node_name=asset.hostname, process_name=app.app_name)
        if not result[0]:
            return Response(dict(data=[{
                'code': 400, 'pid': 0, 'uptime': 0, 'status': result[1], 'id': asset.id, 'messages': ""
            }]))

        data = eval(result, {'true': 0, 'false': 1})
        uptime = data['process']['uptime']
        if uptime == 0:
            stop_time = None
            error = data['process']['statename'] if data['process']['statename'] else data['process']['spawnerr']
            if data['process']['stop']:
                stop_time = translate_timestamp(data['process']['stop'])
            return Response(dict(data=[{
                'code': 400, 'pid': 0, 'uptime': 0, 'status': error, 'id': asset.id, 'messages': 'stop time: '+stop_time
            }]))

        elif ':' in uptime:
            uptime += ' '
        else:
            uptime += ' days'

        data = [
            {
                'code': 200,
                'pid': data['process']['pid'],
                'uptime': uptime,
                'status': data['process']['statename'],
                'id': asset.id,
                'messages': 'start time: '+translate_timestamp(data['process']['start'])
            },
        ]
        logger.info(data)
        return Response(dict(data=data))


class StartAppApi(RetrieveAPIView):

    queryset = DeployList.objects.all()
    permission_classes = (IsValidUser,)

    @staticmethod
    def start_app(hostname, app_name):
        cesi = CesiAPI()
        # cesi.login()
        return cesi.start_process(node_name=hostname, process_name=app_name)

    def retrieve(self, request, *args, **kwargs):

        asset = Asset.objects.get(id=request.GET.get('host_id'))
        app = DeployList.objects.get(id=request.GET.get('app_id'))

        result = StartAppApi.start_app(hostname=asset.hostname, app_name=app.app_name)
        if not result[0]:
            return Response(dict(code=400, message=result[1]))

        result = eval(result, {'true': 0, 'false': 1})

        if result['status'] == 'success':
            return Response(dict(code=200, message=result['message']))
        else:
            return Response(dict(code=400, message=""))


class StopAppApi(RetrieveAPIView):

    queryset = DeployList.objects.all()
    permission_classes = (IsValidUser,)

    @staticmethod
    def stop_app(hostname, app_name):
        cesi = CesiAPI()
        # cesi.login()
        return cesi.stop_process(node_name=hostname, process_name=app_name)

    def retrieve(self, request, *args, **kwargs):

        asset = Asset.objects.get(id=request.GET.get('host_id'))
        app = DeployList.objects.get(id=request.GET.get('app_id'))

        result = StopAppApi.stop_app(hostname=asset.hostname, app_name=app.app_name)
        if not result[0]:
            return Response(dict(code=400, message=result[1]))

        result = eval(result, {'true': 0, 'false': 1})

        if result['status'] == 'success':
            return Response(dict(code=200, message=result['message']))
        else:
            return Response(dict(code=400, message=""))


class ReStartAppApi(RetrieveAPIView):

    queryset = DeployList.objects.all()
    permission_classes = (IsValidUser,)

    @staticmethod
    def restart_app(hostname, app_name):
        cesi = CesiAPI()
        # cesi.login()
        return cesi.restart_process(node_name=hostname, process_name=app_name)

    def retrieve(self, request, *args, **kwargs):

        asset = Asset.objects.get(id=request.GET.get('host_id'))
        app = DeployList.objects.get(id=request.GET.get('app_id'))

        result = ReStartAppApi.restart_app(hostname=asset.hostname, app_name=app.app_name)
        if not result[0]:
            return Response(dict(code=400, message=result[1]))

        result = eval(result, {'true': 0, 'false': 1})

        if result['status'] == 'success':
            return Response(dict(code=200, message=result['message']))
        else:
            return Response(dict(code=400, message=""))


class GetAPPLogApi(RetrieveAPIView):

    queryset = DeployList.objects.all()
    permission_classes = (IsValidUser,)

    @staticmethod
    def get_log(hostname, app_name):
        cesi = CesiAPI()
        return cesi.read_process_log(hostname, app_name)

    def retrieve(self, request, *args, **kwargs):

        asset = Asset.objects.get(id=request.GET.get('host_id'))
        app = DeployList.objects.get(id=request.GET.get('app_id'))

        try:
            result = GetAPPLogApi.get_log(hostname=asset.hostname, app_name=app.app_name)
            result = eval(result, {'true': 0, 'false': 1})
            logs = result["logs"]["stdout"]
            return Response(dict(code=200, message=logs))
        except BaseException as error:
            logger.error(error)
            return Response(dict(code=400, message=str(error)))


class DevOpsAssetViewSet(AssetViewSet):
    permission_classes = (IsValidUser,)
