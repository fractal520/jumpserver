# encoding: utf-8

import tarfile
import os
from common.utils import get_logger
from .models.deploy_list import DeployList, DeployVersion

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
        logger.info('清空资产{}的{}应用版本{}'.format(asset, app.app_name, version.version))
        return True
    except BaseException as error:
        logger.error(error)
        logger.error('删除资产{}应用{}版本失败'.format(asset, app.app_name))
        return False


def add_asset_version(asset, version):
    logger.debug(version)
    try:
        version = DeployVersion.objects.get(version=version)
        version.assets.add(asset)
        logger.info('资产{}添加版本{}成功'.format(asset, version.version))
        return True
    except BaseException as error:
        logger.error(error)
        return False
