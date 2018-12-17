# !/usr/bin/env python
# encoding: utf-8
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from assets.models import Asset


class Command(BaseCommand):

    def __init__(self):
        self.rcs_ip = '192.168.0.127'
        self.rcs_log_dir = '/scss/logs/rcs/'

    def handle(self, *args, **options):
        yestarday = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
        log_path = os.path.join(self.rcs_log_dir, 'rcs.', yestarday, '.log')
        rcs = Asset.objects.get(ip=self.rcs_ip)
        print(rcs.admin_user)
        print("hello world!")
