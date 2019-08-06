#  encoding: utf-8
import json
import re
import os

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext as _

from assets.models import Asset
from common.utils import get_logger
from deploy.util import after_deploy, get_jms_ip
from devops.utils import create_playbook_task
from devops.models import AnsibleRole
from devops.tasks import run_ansible_task
# from assets.models import AdminUser, Asset
from .models import get_deploy_file_path, get_remote_data_path, get_version, get_deploy_jar_path, get_last_version, \
    save_backup_path, get_backup_path, get_version_path, get_backup_directory, update_deploy_info
from . import const

CREATE_PROJECT_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'create_project_dir.sh')
CHOWN_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'chown.sh')
COMPRESS_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'compress_tar.sh')
BACKUP_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'backup.sh')
UNPACK_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'unpack.sh')
DELETEFILE_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'deletefile.sh')


logger = get_logger('jumpserver')


# just for test #
@shared_task
def test_ansible_ping(asset):
    task_name = _("test ansible ping {}".format(asset.hostname))
    return test_ansible_ping_util(asset, task_name)


@shared_task
def test_ansible_ping_util(asset, task_name):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset]
    tasks = const.TEST_CONN_TASKS
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result, summery = task.run()
    return result


# deploy check file exist #
@shared_task
def check_asset_file_exist(asset, app_name):
    task_name = _("check {0} {1} exist {2}".format(asset, app_name, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return check_asset_file_exist_util(asset, app_name, task_name)


@shared_task
def check_asset_file_exist_util(asset, app_name, task_name):
    from ops.utils import update_or_create_ansible_task
    logger.info('检查{0}是否已存在{1}应用启动文件'.format(asset.hostname, app_name))
    hosts = [asset]
    tasks = const.CHECK_FILE_TASK
    tasks[0]['action']['args'] = "ls -la /etc/supervisor/config.d/{}.ini".format(app_name)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    return result


# deploy function #
@shared_task
def push_build_file_to_asset_manual(asset, app_name, user):
    task_name = _("push {0} build file to {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return push_build_file_to_asset_util(asset, task_name, app_name, user)


@shared_task
def push_build_file_to_asset_util(asset, task_name, app_name, user):
    from ops.utils import update_or_create_ansible_task
    ip = get_jms_ip()
    if not ip:
        return

    hosts = [asset]
    tasks = const.COPY_FILE_TO_TASK
    # tasks[0]['action']['args'] = "creates=/data/{0} {1} {2}".format(app_name, CREATE_PROJECT_SCRIPT_DIR, app_name)
    tasks[0]['action']['args'] = {'creates': '/data/{0}'.format(app_name), '_raw_params':  '{0} {1}'.format(CREATE_PROJECT_SCRIPT_DIR, app_name)}
    # tasks[1]['action']['args'] = "{0} {1}".format(DELETEFILE_SCRIPT_DIR, get_deploy_file_path(app_name))

    """
    tasks[2]['action']['args'] = "src={0} dest={1} compress=no".format(
        get_deploy_file_path(app_name),
        get_deploy_file_path(app_name)
    )

    tasks[2]['action']['args'] = "wget http://{0}/download/{1} -O {2}".format(
        ip,
        get_deploy_file_path(app_name).replace('/deploy/', ''),
        get_deploy_file_path(app_name)
    )
    """
    tasks[1]['action']['args'] = "path={0} state=absent".format(get_remote_data_path(app_name))
    tasks[2]['action']['args'] = "{0} {1} {2}".format(COMPRESS_SCRIPT_DIR, app_name, get_version(app_name))
    tasks[3]['action']['args'] = "src={0} state=link path={1}".format(
        get_deploy_jar_path(app_name),
        get_remote_data_path(app_name)
    )
    tasks[4]['action']['args'] = "{0} {1}".format(CHOWN_SCRIPT_DIR, app_name)
    tasks[5]['action']['args'] = "supervisorctl {0} {1}".format('restart', app_name)
    tasks[6]['action']['args'] = "supervisorctl {0} {1}".format('update', app_name)
    logger.debug(tasks)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by=user.name
    )

    # result = task.run()
    result = run_ansible_task(str(task.id))
    if settings.DEPLOY_CELERY == "on":
        return after_deploy(result, task.get_latest_adhoc(), app_name, asset, user)

    return result, task.get_latest_adhoc()

# copy file function
@shared_task
def rsync_file(asset, app_name):
    task_name = _(
        "rsync {0} on {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return rsync_file_util(asset, task_name, app_name)


@shared_task
def rsync_file_util(asset, task_name, app_name):
    from ops.utils import update_or_create_ansible_task
    logger.info("开始发送打包文件")
    hosts = [asset]
    tasks = [
        {
            "name": "开始发送打包文件",
            "action": {
                "module": "copy",
                "args": "src={0} dest={1}".format(
                    get_deploy_file_path(app_name),
                    get_deploy_file_path(app_name)
                )
            }
        }
    ]
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )
    result = task.run()
    if result[1]['dark']:
        return False
    logger.info("文件推送完成")
    return True


# backup function #
@shared_task
def backup_asset_app_file(asset, app_name):
    task_name = _("backup {0} on {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return backup_asset_app_file_util(asset, task_name, app_name)


@shared_task
def backup_asset_app_file_util(asset, task_name, app_name):
    from ops.utils import update_or_create_ansible_task
    version = get_last_version(app_name, asset)
    logger.debug(task_name)
    logger.debug(version)
    if not version:
        logger.info("no version history found {0}".format(app_name))
        return False
    hosts = [asset]
    tasks = const.BACKUP_FILE
    tasks[0]['action']['args'] = "{0} {1} {2}".format(BACKUP_SCRIPT_DIR, app_name, version)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    if result[1]['dark']:
        logger.info('{0} Backup Failed! {1}'.format(app_name, result[1]['dark']))
        return result[1]['dark']

    if not save_backup_path(app_name, version):
        return False
    logger.info('{0} backup complete.'.format(version))

    return result


# rollback version
def rollback_asset_app_version_manual(asset, app_name, version):
    task_name = _("backup {0} on {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return rollback_asset_app_version_util(asset, task_name, app_name, version)


def rollback_asset_app_version_util(asset, task_name, app_name, version):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset]
    tasks = const.ROLLBACK_TASK
    # unpack
    tasks[0]['action']['args'] = "{0} {1} {2} {3}".format(
        UNPACK_SCRIPT_DIR,
        get_backup_path(app_name, version),
        get_backup_directory(app_name, version),
        app_name
    )

    # remove link
    tasks[1]['action']['args'] = "path={0} state=absent".format(get_remote_data_path(app_name))
    # create new link
    tasks[2]['action']['args'] = "src={0} state=link path={1}".format(
        os.path.join(get_version_path(app_name, version), app_name+'.jar'),
        get_remote_data_path(app_name)
    )

    tasks[3]['action']['args'] = "{0} {1}".format(
        CHOWN_SCRIPT_DIR,
        app_name
    )

    tasks[4]['action']['args'] = "supervisorctl {0} {1}".format("restart", app_name)

    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()
    deploy_file_path = get_version_path(app_name, version)
    if result[0]['ok']:
        update_deploy_info(app_name, deploy_file_path)

    # logger.info(result[0]['ok'])
    return result, task.get_latest_adhoc()


# rollback check backupfile exist
def rollback_check_backup_file_exist(asset, app_name, version):
    task_name = _("rollback {0} on {1} {2}".format(version, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return rollback_check_backup_file_exist_util(asset, task_name, app_name, version)


def rollback_check_backup_file_exist_util(asset, task_name, app_name, version):
    from ops.utils import update_or_create_ansible_task
    simple_result = None
    backup_path = get_backup_path(app_name, version)
    if not backup_path:
        return False
    tasks = const.CHECK_FILE_TASK
    hosts = [asset]
    tasks[0]['action']['args'] = "if [ -f '{0}' ]; then echo 'exist'; else echo 'not'; fi".format(backup_path)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    if result[1]['dark']:
        logger.error(result[1]['dark'])
        return False
    if result[0]['ok']:
        logger.debug(result[0]['ok'])
        simple_result = result[0]['ok'][asset.fullname]['检查文件是否存在']['stdout']

    logger.info(simple_result)

    return simple_result, task.get_latest_adhoc()


def push_app_startup_config_file(asset, app_name, java_opts=None, dloader_path=None):
    DEFAULT_JAVA_OPTS = ""
    DEFAULT_DLOADER_PATH = "lib/"
    if not java_opts:
        java_opts = DEFAULT_JAVA_OPTS
    if not dloader_path:
        dloader_path = DEFAULT_DLOADER_PATH
    logger.debug(java_opts)
    logger.debug(dloader_path)
    try:
        ansible_role = AnsibleRole.objects.get(name='addsvapp')
    except BaseException as error:
        logger.debug(error)
        logger.error("请先安装addsvapp的play role!")
        return False
    assets = Asset.objects.filter(hostname=asset.hostname)
    return create_playbook_task(
        assets=assets,
        task_name="push_app_startup_config_file",
        extra_vars={'APP_NAME': app_name, 'JAVA_OPTS': java_opts, 'DLOADER_PATH': dloader_path},
        description="push_{}_startup_config_file to {}".format(app_name, asset.hostname),
        ansible_role=ansible_role,
        run_as_admin=True,
        run_as=""
    )
