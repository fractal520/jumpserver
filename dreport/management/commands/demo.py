# !/usr/bin/env python
# encoding: utf-8
import os
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from assets.models import Asset
from dreport.models.city import CityMonthRecord, CityPauseRecord, City
from dreport.tasks import collect_risk_manual


class Command(BaseCommand):

    def __init__(self):
        self.rcs_ip = '192.168.0.127'
        self.rcs_log_dir = '/scss/logs/rcs/'

    def handle(self, *args, **options):
        yestarday = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
        log_path = os.path.join(self.rcs_log_dir, 'rcs.', yestarday, '.log')
        rcs = Asset.objects.get(ip=self.rcs_ip)
        print(rcs.admin_user)

        result = collect_risk_manual(asset=rcs, script_path='/home/jumperserver/RA.py')
        print(result)
        if result[0]['ok']:
            data = result[0]['ok'][rcs.hostname]
            for key, value in data.items():
                stout = json.loads(value.get('stdout'))
                print(stout.get('risk_list'))
                if CityPauseRecord.add_record(risk_list=stout.get('risk_list', None)):
                    print('添加成功')
                print('添加失败')
                print(stout)
