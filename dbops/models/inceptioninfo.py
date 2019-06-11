# -*- coding: utf-8 -*-
#

from django.db import models


class InceptionInfo(models.Model):

    id = models.AutoField(primary_key=True)
    host = models.GenericIPAddressField(max_length=32)
    port = models.CharField(max_length=32)
    user = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    back_host = models.GenericIPAddressField(max_length=32)
    back_port = models.CharField(max_length=32)
    back_user = models.CharField(max_length=32)
    back_password = models.CharField(max_length=32)

    def __str__(self):
        return "InceptionInfo"
