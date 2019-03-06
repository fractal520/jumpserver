from django.db import models
from django.utils.translation import ugettext_lazy as _
from assets.models import Asset, Node, SystemUser
from common.utils import get_signer, get_logger
from ops.models import Task, AdHoc, AdHocRunHistory

logger = get_logger(__file__)

__all__ = ["AnsibleRole", "PlayBookTask", "Playbook"]


class AnsibleRole(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))

    def __str__(self):
        return str(self.name)


class PlayBookTask(Task):
    desc = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    password = models.CharField(max_length=200, verbose_name=_('WebHook Password'), blank=True, null=True)
    extra_vars = models.CharField(max_length=512, verbose_name=_('Extra Vars'), blank=True, null=True)
    ansible_role = models.ForeignKey(
        AnsibleRole, verbose_name=_('Ansible Role'), related_name='task', on_delete=models.DO_NOTHING
    )
    tags = models.TextField(verbose_name=_('Tags'), null=True, blank=True, default=['all'])
    assets = models.ManyToManyField(Asset, verbose_name=_('Assets'), related_name='task', blank=True)
    groups = models.ManyToManyField(Node, verbose_name=_('Asset Groups'), related_name='task', blank=True)
    system_user = models.ForeignKey(SystemUser, null=True, blank=True, verbose_name=_('System User'),
                                    related_name='task', on_delete=models.DO_NOTHING)


class Playbook(AdHoc):
    playbook_path = models.CharField(max_length=1000, verbose_name=_('Playbook Path'), blank=True, null=True)
    is_running = models.BooleanField(default=False, verbose_name=_('Is running'))
