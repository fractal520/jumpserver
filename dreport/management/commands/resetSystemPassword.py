# !/usr/bin/env python
# encoding: utf-8
import os
import json
import random
import csv
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from common.utils import get_logger
from assets.models import Asset, AdminUser


logger = get_logger('jumpserver')


@shared_task
def modify_asset_root_password(asset, password):
    task_name = ("Reset {} root password {}.".format(asset.hostname, password))
    return modify_asset_root_password_util(asset, password, task_name)


@shared_task
def modify_asset_root_password_util(asset, password, task_name):
    from ops.utils import update_or_create_ansible_task
    hosts = [asset.fullname]

    password = "{{ '{}' | password_hash('sha512') }}".format(password)

    tasks = [
        {
            "name": "Reset asset root password",
            "action": {
                "module": "user",
                "args": "name=root password={} update_password=always".format(password),
            }
        }
    ]

    TASK_OPTIONS = {
        'timeout': 10,
        'forks': 10,
    }

    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    print(tasks)

    return task.run()


class PassManager(object):

    def __init__(self):
        self.word_up = [chr(i) for i in range(ord("A"), ord("Z")+1)]
        self.word_low = [chr(i) for i in range(ord("a"), ord("z")+1)]

    def generate_password(self, num=0, word=0):
        pass_li = []

        for num in range(num):
            pass_li.append(str(random.randint(1, 10)))

        up = random.randint(1, word-1)
        low = word - up

        pass_li += random.sample(self.word_up, up)
        pass_li += random.sample(self.word_low, low)
        random.shuffle(pass_li)
        password = ''.join(pass_li)
        print(password)
        return password

    def modify_password(self, assets):
        with open('./savePassword.csv', 'wt', newline='') as fhandler:
            writer = csv.writer(fhandler)
            for asset in assets:
                password = self.generate_password(num=4, word=6)
                result = modify_asset_root_password(asset, password)
                print(result)
                writer.writerow([asset.hostname, 'root', password, asset.ip, 'new'])


class Command(BaseCommand):

    def __init__(self):
        try:
            self.admin = AdminUser.objects.get(name='wtsd')
        except ObjectDoesNotExist as error:
            self.admin = None
            logger.error(error)

    def handle(self, *args, **options):
        if not self.admin:
            return False
        # assets = Asset.objects.filter(platform="Linux", admin_user=self.admin)
        assets = Asset.objects.filter(ip="192.168.0.127")
        pm = PassManager()
        pm.modify_password(assets)
