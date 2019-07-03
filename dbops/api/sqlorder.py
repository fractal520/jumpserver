# encoding: utf-8
#

from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from dbops.lib import call_inception
from apps.common.utils import get_logger
from dbops.models.dbinfo import DbInfo
from dbops.task import ExecSql
from dbops.models.sqlinfo import SqlOrder, SqlRecord
from dbops.genrollbacksql import GenRollBackSql
from dbops.serializer import SqlOrderSerializers
import traceback
from common.permissions import IsOrgAdminOrAppUser, IsValidUser


logger = get_logger('jumpserver')


class Check(APIView):

    permission_classes = (IsValidUser, )

    def post(self, request):
        try:
            id = int(request.data['id'])
            sql = request.data['sql']
            sql = str(sql).strip('\n').strip().rstrip(';')
            data = DbInfo.objects.filter(id=id).first()
            info = {
                'host': data.ip,
                'user': data.username,
                'password': data.password,
                'db': data.db_name,
                'port': data.port
            }
        except KeyError as e:
            logger.error(f'{e.__class__.__name__}: {e}')
        else:
            try:
                with call_inception.Inception(LoginDic=info) as test:
                    res = test.Check(sql=sql)
                    return Response({'result': res, 'status': 200})
            except Exception as e:
                traceback.print_exc()
                logger.error(f'{e.__class__.__name__}: {e}')
                return Response(str(e))


class Audit(UpdateAPIView):

    permission_classes = (IsValidUser,)
    queryset = SqlOrder.objects.all()
    serializer_class = SqlOrderSerializers
    lookup_field = 'work_id'

    def update(self, request, *args, **kwargs):
        sqlorder = self.get_object()
        sqlorder.status = int(request.data.get("status"))
        sqlorder.save()
        return Response({'status': 200})


class Exec(APIView):

    permission_classes = (IsValidUser,)

    def get(self, request, pk):
        work_id = pk
        sqlorder = SqlOrder.objects.filter(work_id=work_id).first()
        data = {
            'work_id': sqlorder.work_id,
            'text': sqlorder.text,
            'sql': sqlorder.sql.split(';'),
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


class RollBack(APIView):

    permission_classes = (IsValidUser,)

    def get(self, request, pk):
        work_id = pk
        db = SqlOrder.objects.filter(work_id=work_id).first().dbinfo.db_name
        sqlrecord = SqlRecord.objects.filter(work_id=work_id).all()
        rollback_sql = []
        for r in sqlrecord:
            if r.backup_dbname != 'None':
                with GenRollBackSql(r.backup_dbname, r.sequence) as gen:
                    back_table = gen.get_back_table()
                    if back_table:
                        sql = gen.get_rollback_sql(back_table)
                        for s in sql:
                            rollback_sql.append(s)
        rollback_sql.sort(key=lambda x: x[1], reverse=True)
        if rollback_sql:
            rollback_sql = [x[0] for x in rollback_sql]
        else:
            rollback_sql = ["没有备份或语句执行失败!"]
        return Response({'db': db, 'rollback_sql': rollback_sql})
