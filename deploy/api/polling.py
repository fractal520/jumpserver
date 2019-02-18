# encoding: utf-8

from time import sleep
from ..pjenkins.exec_jenkins import JenkinsWork
from common.utils import get_logger

logger = get_logger('jumpserver')


def first_polling(request):
    jw = JenkinsWork()
    MAX_COUNT = 100
    polling_count = 0
    while polling_count < MAX_COUNT:
        print(polling_count)
        result = jw.collect_job(name='MPS')

        if result['build_status'] == "SUCCESS":
            logger.debug('polling build_status SUCCESS continue')
        if result['build_status'] == "RUNNING":
            return "RUNNING"
        if result['build_status'] == "FAILURE":
            return "FAILURE"
        polling_count += 1
        sleep(2)

    return "TIME OUT FAILURE"


def sec_polling(request):
    jw = JenkinsWork()
    MAX_COUNT = 100
    polling_count = 0
    while polling_count < MAX_COUNT:
        print(polling_count)
        result = jw.collect_job(name='MPS')

        if result['build_status'] == "SUCCESS":
            return "SUCCESS"
        if result['build_status'] == "RUNNING":
            logger.debug('polling build_status RUNNING continue')
        if result['build_status'] == "FAILURE":
            return "FAILURE"
        polling_count += 1
        sleep(2)

    return "TIME OUT FAILURE"

