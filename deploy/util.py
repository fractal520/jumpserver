# encoding: utf-8


import tarfile
import os
import socket
from django.utils import timezone
from common.utils import get_logger
from .models.deploy_list import DeployList, DeployVersion
from deploy.models import add_version_list, DeployRecord

logger = get_logger('jumpserver')


def pack_up_deploy_file(app_name, only_jar=True):
    app = DeployList.objects.get(app_name=app_name)
    deploy_file_path = app.deploy_file_path
    app_version = deploy_file_path.split('/')[-1]
    conf_dir = 'deploy/{0}/app/{1}/config'.format(app_name, app_version)
    lib_dir = 'deploy/{0}/app/{1}/lib'.format(app_name, app_version)

    if only_jar:
        exclude_names = [conf_dir, lib_dir]
    else:
        exclude_names = [conf_dir]

    t = tarfile.open(os.path.join(DeployList.DEPLOY_FILE_DIR, app_name, 'app', app_version+'.tar.gz'), "w:gz")
    try:
        t.add(
            os.path.join(DeployList.DEPLOY_FILE_DIR, app_name, 'app', app_version),
            filter=lambda x: None if x.name in exclude_names else x
        )
    except BaseException as error:
        logger.error(error)
        return False

    return True


def clean_asset_version(asset, app):
    try:
        version = asset.deployversion_set.all().filter(app_name=app)[0]
        asset.deployversion_set.remove(version)
        # print('清空资产{}的{}应用版本{}'.format(asset, app.app_name, version.version))
        logger.info('清空资产{}的{}应用版本{}'.format(asset, app.app_name, version.version))
        return True
    except BaseException as error:
        logger.error(error)
        # print('删除资产{}应用{}版本失败'.format(asset, app.app_name))
        logger.error('删除资产{}应用{}版本失败'.format(asset, app.app_name))
        return False


def add_asset_version(asset, version):
    logger.debug(version)
    try:
        version = DeployVersion.objects.get(version=version)
        version.assets.add(asset)
        # print('资产{}添加版本{}成功'.format(asset, version.version))
        logger.info('资产{}添加版本{}成功'.format(asset, version.version))
        return True
    except BaseException as error:
        logger.error(error)
        return False


def after_deploy(task, last_adhoc, app_name, asset, user):
    last_history = last_adhoc.latest_history
    logger.debug(last_history)
    job = DeployList.objects.get(app_name=app_name)
    if task[1]['dark']:
        job.published_status = False
        job.save()
        # 生成版本号
        version = add_version_list(app_name, version_status=False)
        # print('发布失败，请查看错误信息 {0}'.format(task[1]['dark']))
        logger.error('发布失败，请查看错误信息 {0}'.format(task[1]['dark']))
        # 发布记录
        clean_asset_version(asset, DeployList.objects.get(app_name=app_name))
        add_asset_version(asset, version.version)
        DeployRecord.add_record(asset, app_name, version, result=False, user=user, history=last_history)
        return dict(code=400, error=task[1]['dark'])
    elif task[0]['ok']:
        job.published_time = timezone.now()
        job.published_status = True
        job.save()
        # 生成版本号
        version = add_version_list(app_name)
        # print('应用{0}成功发布到{1}'.format(app_name, asset.hostname))
        logger.info('应用{0}成功发布到{1}'.format(app_name, asset.hostname))

        try:
            logger.debug(user)
        except BaseException as error:
            logger.debug(error)

        # 发布记录
        try:
            DeployRecord.add_record(asset, app_name, version, user=user, history=last_history)
            clean_asset_version(asset, DeployList.objects.get(app_name=app_name))
            add_asset_version(asset, version.version)
        except BaseException as error:
            logger.error(error)
        return dict(code=200, task=task)
    else:
        # print("升级失败 {0}".format(task))
        logger.error("升级失败 {0}".format(task))
        return dict(code=400, error="升级失败,请回滚")


def get_jms_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 8080))
        return s.getsockname()[0]
    except BaseException as error:
        logger.error(str(error))
        logger.error("获取IP地址失败，请重试或检查网络状况!")
        return False
