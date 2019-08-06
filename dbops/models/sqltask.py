# -*- coding: utf-8 -*-
#

from django.db import models
from common.utils import get_logger


logger = get_logger('jumpserver')


class SqlTask(models.Model):

    task_id = models.UUIDField(db_index=True)
    sid = models.CharField(max_length=20)
    svn_path = models.CharField(max_length=512, db_index=True)
    sql_file_path = models.CharField(max_length=512)
    sql_file_name = models.CharField(max_length=512, db_index=True)
    work_id = models.CharField(max_length=50)  # 任务ID

    def __str__(self):
        return self.task_id

