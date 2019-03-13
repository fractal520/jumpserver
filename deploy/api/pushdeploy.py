# encoding: utf-8

from django.utils import timezone
from django.core import serializers

from ..models import DeployList, DeployVersion, add_version_list, turn_build_file_to_deploy, DeployRecord
from assets.models import AdminUser, Asset
from common.utils import get_logger
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from deploy.tasks import test_ansible_ping, push_build_file_to_asset_manual, \
    backup_asset_app_file, check_asset_file_exist, push_app_startup_config_file
from ..util import pack_up_deploy_file


logger = get_logger('jumpserver')
__all__ = [
    'deploy_file_to_asset',
    'get_version_history'
]


# just for test
def get_host_admin(request):
    print(request.GET)
    host = request.GET.get('task_host')
    try:
        asset = Asset.objects.get(ip=host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))
    task = test_ansible_ping(asset)
    print(task)
    return JsonResponse(dict(code=200, task=task))


def deploy_file_to_asset(request):
    # get information from request and get target host from DB
    host = request.GET.get('task_host')
    app_name = request.GET.get('app_name')
    try:
        asset = Asset.objects.get(id=host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))

    # backup old version on remote host and return result
    backup_result = backup_asset_app_file(asset, app_name)
    if not backup_result:
        logger.info(backup_result)

    # rename build file and return result
    if not turn_build_file_to_deploy(app_name):
        logger.error('找不到{0}构建文件'.format(app_name))
        return JsonResponse(dict(code=400, error='file not found!'))

    # check remote host is already have target APP
    check_result = check_asset_file_exist(asset, app_name)
    # if check_result[0]['ok']:
    #     logger.info('增量打包')
    #     pack_result = pack_up_deploy_file(app_name)
    # else:
    if not check_result[0]['ok']:
        logger.info("应用启动文件不存在，需要推送应用启动文件")
        task = push_app_startup_config_file(asset, app_name)
        if task:
            task.run()

    logger.info('全量打包')
    pack_result = pack_up_deploy_file(app_name, only_jar=False)

    if not pack_result:
        add_version_list(app_name, version_status=False)
        logger.error('文件打包失败')
        return JsonResponse(dict(code=400, error='文件打包失败'))

    # use ansible to push APP to remote host
    task = push_build_file_to_asset_manual(asset, app_name)
    job = DeployList.objects.get(app_name=app_name)
    if task[1]['dark']:
        job.published_status = False
        job.save()
        add_version_list(app_name, version_status=False)
        logger.error('发布失败，请查看错误信息 {0}'.format(task[1]['dark']))
        return JsonResponse(dict(code=400, error=task[1]['dark']))
    elif task[0]['ok']:
        job.published_time = timezone.now()
        job.published_status = True
        job.save()
        version = add_version_list(app_name)
        logger.info('应用{0}成功发布到{1}'.format(app_name, asset.hostname))
        try:
            DeployRecord.add_record(asset, app_name, version)
        except BaseException as error:
            logger.error(error)
        return JsonResponse(dict(code=200, task=task))
    else:
        logger.error("升级失败 {0}".format(task))
        return JsonResponse(dict(code=400, error="升级失败,请回滚"))


# ajax get version list object
def get_version_history(request):
    app_id = request.GET.get('id')
    version = serializers.serialize(
        "json",
        DeployVersion.objects.filter(app_name_id=app_id).order_by('-create_time')[:5]
    )
    return HttpResponse(version)
