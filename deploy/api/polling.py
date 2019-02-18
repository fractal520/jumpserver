# encoding: utf-8

from ..pjenkins.exec_jenkins import JenkinsWork
from common.utils import get_logger

logger = get_logger('jumpserver')


def polling(request):
    jw = JenkinsWork()
    result = jw.collect_job(name='MPS')
    print(result)
