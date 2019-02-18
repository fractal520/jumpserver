# encoding: utf-8

from time import sleep
from django.http import JsonResponse
from ..pjenkins.exec_jenkins import JenkinsWork
from common.utils import get_logger
from ..models import DeployList, create_or_update

logger = get_logger('jumpserver')


def polling(request):
    print(request.GET)
    jw = JenkinsWork()
    id = request.GET.get('id')
    is_first = request.GET.get('is_first')
    app = DeployList.objects.get(id=id)
    MAX_COUNT = 100
    polling_count = 0
    print(id, is_first)
    while polling_count < MAX_COUNT:
        print(polling_count)
        result = jw.collect_job(name=app.app_name)
        print(result['build_status'])
        if result['build_status'] == "SUCCESS":
            if is_first:
                logger.debug('polling build_status SUCCESS continue')
            if not is_first:
                create_or_update([{
                    'name': result.app_name,
                    'last_build_time': result.last_build_time,
                    'build_console_output': result.last_build_console,
                    'last_success_build_num': result.last_success_build_num,
                    'last_build_num': result.last_build_num,
                    'build_status': result.build_status

                }])
                return JsonResponse(dict(code=200, msg="SUCCESS"))
        if result.get('build_status') == "RUNNING":
            if is_first:
                return JsonResponse(dict(code=200, msg="RUNNING"))
            if not is_first:
                logger.debug('polling build_status RUNNING continue')
        if result['build_status'] == "FAILURE":
            return JsonResponse(dict(code=200, error="FAILURE"))
        polling_count += 1
        sleep(2)

    return JsonResponse(dict(code=200, data="TIME OUT FAILURE"))
