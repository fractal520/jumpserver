import uuid
from django.db import models

from ops.models import AdHoc
from devops.models import PlayBookTask
from common.utils import get_logger
from deploy.models import DeployVersion

logger = get_logger(__file__)


class MainTask(models.Model):
    """
    任务中心: 任务列表
    """
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, unique=True, verbose_name="任务名称")
    desc = models.TextField(null=True, blank=True, verbose_name="任务简要")
    adhoc_task = models.ManyToManyField(AdHoc, blank=True, verbose_name="Ansible AdHoc任务")
    playbook_task = models.ManyToManyField(PlayBookTask, blank=True, verbose_name="Ansible Playbook任务")
    version = models.ForeignKey(DeployVersion, null=True, blank=True, on_delete=models.DO_NOTHING, verbose_name="任务版本")

    def __str__(self):
        return "{}:{}".format(self.name, self.version.version)

    class Meta:
        verbose_name = "任务列表"
        verbose_name_plural = verbose_name
