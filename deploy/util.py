# encoding: utf-8

import tarfile
import os
from .models.deploy_list import DeployList


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
        return False

    return True
