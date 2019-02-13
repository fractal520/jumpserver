# !/usr/bin/env python
# encoding: utf-8
import os
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from common.utils import get_logger
from assets.models import Asset
from dreport.models.city import CityMonthRecord, CityPauseRecord, City
from dreport.tasks import collect_risk_manual

logger = get_logger('jumpserver')


class Command(BaseCommand):

    def __init__(self):
        self.rcs_ip = '10.10.3.46'
        self.rcs_log_dir = '/scss/logs/rcs/'

    def handle(self, *args, **options):
        yestarday = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
        log_path = os.path.join(self.rcs_log_dir, 'rcs.', yestarday, '.log')
        logger.info('获取风控服务器信息')
        try:
            rcs = Asset.objects.get(ip=self.rcs_ip)
        except ObjectDoesNotExist as error:
            logger.error(error)

        logger.info('开始从{}获取{}熔断信息'.format(rcs.hostname, yestarday))
        result = collect_risk_manual(asset=rcs, script_path='/opt/CronScript/RA.py')
        if result[0]['ok']:
            data = result[0]['ok'][rcs.hostname]
            for key, value in data.items():
                stout = json.loads(value.get('stdout'))
                if CityPauseRecord().add_record(
                        risk_list=stout.get('risk_list', None),
                        risk_date=stout.get('date', None)
                ):
                    logger.info('添加成功')
                    logger.info(stout)
                else:
                    logger.error('添加失败')
                    logger.error(stout)
