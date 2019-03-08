import uuid
import json
import os
import yaml
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from common.utils import get_signer, get_logger
from ops.ansible.runner import get_default_options, PlayBookRunner
from ops.inventory import JMSInventory
from ops.ansible import AnsibleError
from assets.models import Asset

logger = get_logger(__file__)

__all__ = ["AnsibleRole", "PlayBookTask"]

playbook_dir = os.path.join(settings.PROJECT_DIR, 'data', 'playbooks')

if not os.path.isdir(playbook_dir):
    os.makedirs(playbook_dir)


class AnsibleRole(models.Model):

    name = models.CharField(max_length=200, verbose_name=_('Name'))

    def __str__(self):
        return str(self.name)


class PlayBookTask(models.Model):

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, unique=True, verbose_name=_('Name'))
    created_by = models.CharField(max_length=128, blank=True, null=True, default='')
    date_created = models.DateTimeField(auto_now_add=True)
    desc = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    ansible_role = models.ForeignKey(
        AnsibleRole, verbose_name=_('Ansible Role'), related_name='task', on_delete=models.DO_NOTHING
    )
    run_as_admin = models.BooleanField(default=False, verbose_name=_('Run as admin'))
    run_as = models.CharField(max_length=128, default='', verbose_name=_("Run as"))
    playbook_path = models.CharField(max_length=1000, verbose_name=_('Playbook Path'), blank=True, null=True)
    is_running = models.BooleanField(default=False, verbose_name=_('Is running'))
    extra_vars = models.CharField(max_length=512, verbose_name=_('Extra Vars'), blank=True, null=True)
    assets = models.ManyToManyField('assets.Asset', blank=True, verbose_name=_("Assets"))
    _hosts = models.TextField(blank=True, verbose_name=_('Hosts'))  # ['hostname1', 'hostname2']

    @property
    def hosts(self):
        return json.loads(self._hosts)

    @hosts.setter
    def hosts(self, item):
        self._hosts = json.dumps(item)

    # 获取默认options
    @property
    def options(self):
        return get_default_options()

    # 使用JMSInventory构建inventory
    @property
    def inventory(self):
        hostname_list = [asset.fullname for asset in self.assets.all()]
        return JMSInventory(
            hostname_list=hostname_list,
            run_as_admin=self.run_as_admin,
            run_as=self.run_as,
            become_info=None
        )

    @property
    def hex_id(self):
        return self.id.hex

    def create_playbook(self, ansible_role):
        self.playbook_path = os.path.join(playbook_dir, self.hex_id)
        yml_tpl = [{'hosts': 'all', 'roles': [{'role': ansible_role.name}]}]
        with open(self.playbook_path, 'wt') as fhandler:
            yaml.dump(yml_tpl, fhandler)
        self.save()
        return True

    def run(self):
        return self._run_only()

    def _run_only(self):
        options = self.options

        self.create_playbook(self.ansible_role)

        # 判断playbook是否存在
        if not os.path.exists(self.playbook_path) or not os.path.isfile(self.playbook_path):
            raise FileNotFoundError('Please check playbook_path {}.'.format(self.playbook_path))

        # 将playbook_path传入options
        options = options._replace(playbook_path=self.playbook_path)
        runner = PlayBookRunner(self.inventory, options=options)

        # 将额外变量传入变量控制器
        if self.extra_vars:
            runner.variable_manager.extra_vars = eval(self.extra_vars)
            logger.debug(json.dumps(runner.variable_manager.get_vars()))
        try:
            result = runner.run()
            self.is_running = True
            self.save()
            logger.debug(result)
            return result
        except AnsibleError as e:
            logger.warn("Failed run playbook {}, {}".format(self.name, e))
            pass
