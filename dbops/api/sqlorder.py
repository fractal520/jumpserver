# encoding: utf-8
#

from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from dbops.lib import call_inception
from apps.common.utils import get_logger
from common.permissions import IsValidUser
from dbops.models.dbinfo import DbInfo
from dbops.task import ExecSql
from dbops.models.sqlinfo import SqlOrder, SqlRecord
import traceback

logger = get_logger('jumpserver')


class Check(APIView):

    def post(self, request):
        try:
            id = int(request.data['id'])
            sql = request.data['sql']
            sql = str(sql).strip('\n').strip().rstrip(';')
            print("sql"+sql)
            data = DbInfo.objects.filter(id=id).first()
            info = {
                'host': data.ip,
                'user': data.username,
                'password': data.password,
                'db': data.db_name,
                'port': data.port
            }
            logger.info("info" + str(info))
        except KeyError as e:
            logger.error(f'{e.__class__.__name__}: {e}')
        else:
            try:
                with call_inception.Inception(LoginDic=info) as test:
                    logger.info("Inception with" + str(test.__dict__))
                    res = test.Check(sql=sql)
                    return Response({'result': res, 'status': 200})
            except Exception as e:
                traceback.print_exc()
                logger.error(f'{e.__class__.__name__}: {e}')
                return Response(str(e))


class Exec(APIView):
    def get(self, request, pk):
        work_id = pk
        sqlorder = SqlOrder.objects.filter(work_id=work_id).first()
        data = {
            'work_id': sqlorder.work_id,
            'text': sqlorder.text,
            'sql': sqlorder.sql,
            'db': sqlorder.dbinfo.db_name,
            'status': sqlorder.get_status_display()
        }
        return Response(data)

    def post(self, request, pk):
        exec_user = request.user
        work_id = pk
        ExecSql(work_id, exec_user).start()
        msg = "SQL任务执行成功!请通过记录页面查看具体执行结果"
        messages.success(request, msg)
        return Response('SQL任务执行成功!请通过记录页面查看具体执行结果')


