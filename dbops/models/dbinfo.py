# -*- coding: utf-8 -*-
#

import os
import shutil
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from assets.models import Asset
from users.models import User
from ops.models import AdHocRunHistory
from common.utils import get_logger
from datetime import datetime


logger = get_logger('jumpserver')


class DbInfo(models.Model):

    id = models.AutoField(primary_key=True)
    db_name = models.CharField(max_length=32, db_index=True)
    instance_name = models.CharField(max_length=32, db_index=True)
    ip = models.GenericIPAddressField(max_length=32, verbose_name=_('IP'), db_index=True)
    port = models.CharField(max_length=32)
    username = models.CharField(max_length=32)  # 连接用户
    password = models.CharField(max_length=32)  # 连接密码

    def __str__(self):
        return self.db_name

