# encoding: utf-8

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from django.utils import timezone
from django.core import serializers
from deploy.models import DeployList, DeployVersion, add_version_list, turn_build_file_to_deploy
from assets.models import AdminUser, Asset
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from ..tasks import rollback_asset_app_version_manual, rollback_check_backup_file_exist
from deploy.util import clean_asset_version, add_asset_version
from common.utils import get_logger

logger = get_logger('jumpserver')


def rollback(request):
    task_host = request.GET.get('task_host')
    try:
        asset = Asset.objects.get(id=task_host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))
    version = request.GET.get('version')
    app_name = request.GET.get('app_name')
    logger.info("{0}的{1} 将回滚到 {2}".format(asset.hostname, app_name, version))
    # check target version backup file exist
    exist_result = rollback_check_backup_file_exist(asset, app_name, version)
    if exist_result == 'not':
        logger.error('{0}{1}备份文件不存在'.format(app_name, version))
        return JsonResponse(dict(code=400, error='{0}{1}备份文件不存在'.format(app_name, version)))
    if not exist_result:
        logger.error('{0}{1}回滚发生未知错误'.format(app_name, version))
        return JsonResponse(dict(code=400, error='unknown error'))

    result = rollback_asset_app_version_manual(asset, app_name, version)

    if result[0]['failed']:
        logger.error("回滚,错误信息:{0}".format(result[0]['failed']))
        return JsonResponse(dict(code=400, error=str(result[0]['failed'])))

    if not clean_asset_version(asset, DeployList.objects.get(app_name=app_name)) or not add_asset_version(asset, version):
        return JsonResponse(dict(code=400, msg=str('版本控制失败,请手动修复资产对应APP版本')))

    logger.info('{0} {1}成功回滚到{2}'.format(asset.hostname, app_name, version))
    return JsonResponse(dict(code=200, msg=str(result)))
