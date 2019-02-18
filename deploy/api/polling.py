# encoding: utf-8

from time import sleep
from django.http import JsonResponse
from ..pjenkins.exec_jenkins import JenkinsWork
from common.utils import get_logger
from ..models import DeployList

logger = get_logger('jumpserver')


def polling(request):
    print(request.POST)
    jw = JenkinsWork()
    id = request.POST.get('id')
    is_first = request.POST.get('is_first')
    app = DeployList.objects.get(id=id)
    MAX_COUNT = 100
    polling_count = 0
    while polling_count < MAX_COUNT:
        print(polling_count)
        result = jw.collect_job(name=app.app_name)

        if result['build_status'] == "SUCCESS":
            if is_first:
                logger.debug('polling build_status SUCCESS continue')
            if not is_first:
                JsonResponse(dict(code=200, msg="SUCCESS"))
        if result['build_status'] == "RUNNING":
            if is_first:
                JsonResponse(dict(code=200, msg="RUNNING"))
            if not is_first:
                logger.debug('polling build_status RUNNING continue')
        if result['build_status'] == "FAILURE":
            JsonResponse(dict(code=200, error="FAILURE"))
        polling_count += 1
        sleep(2)

    JsonResponse(dict(code=200, data="TIME OUT FAILURE"))
