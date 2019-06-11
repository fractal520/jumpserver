# -*- coding: utf-8 -*-
#

from django.db import models
from users.models import User


class SqlOrder(models.Model):
    '''
    SQL任务记录表
    '''
    type_items = [
        (0, 'DDL'),
        (1, 'DML'),
    ]
    backup_items = [
        (0, 'not backup'),
        (1, 'backup'),
    ]

    status_items = [
        (0, '未执行'),
        (1, '驳回'),
        (2, '执行中'),
        (3, '执行成功'),
        (4, '执行失败'),
    ]

    work_id = models.CharField(max_length=50)  # 任务ID
    submit_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='submit_user', verbose_name="提交人")  # 提交人
    insert_date = models.DateTimeField(auto_now_add=True)  # 提交日期
    dbinfo = models.ForeignKey('DbInfo', on_delete=models.PROTECT, verbose_name="数据库")  # 数据库
    sql = models.TextField(verbose_name="SQL语句")  # SQL语句
    status = models.SmallIntegerField(choices=status_items, default=0, verbose_name="任务状态")
    type = models.SmallIntegerField(choices=type_items, verbose_name="语句类型")  # 语句类型 0 DDL 1 DML
    backup = models.SmallIntegerField(choices=backup_items, verbose_name="是否备份")  # 任务是否备份 0 not backup 1 backup
    text = models.CharField(max_length=100, verbose_name="任务说明")  # 任务说明
    exec_time = models.DateTimeField(null=True)  # SQL执行时间
    exec_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='exec_user', null=True, verbose_name="执行人")  # 执行人

    def __str__(self):
        return self.work_id + '_' + str(self.submit_user)


class SqlRecord(models.Model):
    '''
    SQL执行记录表
    '''
    workid = models.CharField(max_length=50)
    state = models.CharField(max_length=100)  # 执行状态
    sql = models.TextField()
    sequence = models.CharField(max_length=50)
    error = models.TextField(null=True)
    affectrow = models.CharField(max_length=100, null=True)
    execute_time = models.CharField(max_length=150, null=True)
    backup_dbname = models.CharField(max_length=100, null=True)
    sqlsha1 = models.TextField(null=True)