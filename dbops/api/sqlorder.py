# encoding: utf-8
#

import os
from os import path, walk
import datetime
import re
from django.contrib import messages
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, CreateAPIView
from rest_framework.response import Response
from apps.common.utils import get_logger
from common.permissions import IsOrgAdminOrAppUser, IsValidUser
from dbops.lib import call_inception
from dbops.lib.util import workid
from dbops.lib.util import get_sql_path
from dbops.lib import svn_co
from dbops.models.dbinfo import DbInfo
from dbops.models.sqlinfo import SqlOrder, SqlRecord
from dbops.models.sqltask import SqlTask
from dbops.task import ExecSql
from dbops.genrollbacksql import GenRollBackSql
from dbops.serializer import SqlOrderSerializers
import traceback

from ..lib.util import workid


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
        sqlorder = SqlOrder.objects.filter(work_id=pk).first()
        if sqlorder.status == 2:
            ExecSql(exec_user, sqlorder).start()
            msg = "SQL任务执行成功!请通过记录页面查看具体执行结果"
            messages.success(request, msg)
            return Response({'status': 200, 'message': msg})
        else:
            msg = "SQL任务状态为" + sqlorder.get_status_display + "，该任务不能执行。"
            return Response({'status': 400, 'message': msg})


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


class Create(APIView):

    permission_classes = (IsValidUser,)

    def post(self, request, args=None):
        sqlorder_list = []
        task_id = request.data.get('task_id')
        svn_path = request.data.get('svn_path')
        file_path_base = '/tmp/'
        file_path = file_path_base + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.makedirs(file_path)
        svn_read = svn_co.svn_co(svn_path=svn_path, file_path=file_path)
        if svn_read[0] == 0:
            sql_path_list = get_sql_path(file_path)
            if sql_path_list:
                for sql_file in sql_path_list:
                    sqlorder_info = {}
                    sql_file_path = os.path.split(sql_file)[0]
                    sql_file_name = os.path.split(sql_file)[-1]
                    logger.info('deal sql file:' + str(sql_file_name))
                    sqlorder_info['task_id'] = task_id
                    sqlorder_info['svn_path'] = svn_path
                    sqlorder_info['sql_file_path'] = sql_file_path
                    sqlorder_info['sql_file_name'] = sql_file_name
                    sql_file_info = re.match(r'(\d+)-(\w+)-(\w+)-(\w+)-(.*)\.sql', sql_file_name)
                    if sql_file_info:
                        sqlorder_info['sid'] = sql_file_info.group(1)
                        db_name = sql_file_info.group(2)
                        try:
                            sqlorder_info['dbinfo'] = DbInfo.objects.get(db_name=db_name)
                        except DbInfo.DoesNotExist:
                            return Response({'status': 500, 'messages': '数据库' + db_name + '不存在，请核实。' + '文件：' + sql_file_name})
                        with open(sql_file, 'r') as f:
                            sql = f.read()
                            sql = re.sub(r'；$', ';', sql)
                            sqlorder_info['sql'] = re.sub(r'\s', ' ', sql)
                        type_name = sql_file_info.group(3).upper()
                        try:
                            sqlorder_info['type'] = SqlOrder.get_type_value(type_name)
                        except KeyError:
                            return Response({'status': 500, 'messages': '类型' + type_name + '不存在，请核实。' + '文件：' + sql_file_name})
                        sqlorder_info['submit_user'] = sql_file_info.group(4)
                        sqlorder_info['text'] = sql_file_info.group(5)
                    else:
                        return Response({'status': 500, 'messages': '文件' + sql_file_name + '命名不正确，请核实。'})
                    sqlorder_info['work_id'] = workid()
                    sqlorder_info['create_user'] = request.user
                    sqlorder_info['backup'] = 0
                    sqlorder_list.append(sqlorder_info)
            else:
                return Response({'status': 500, 'messages': '没有发现SQL文件'})
        else:
            return Response({'status': 500, 'messages': 'checkout ' + svn_path + ' errer.'})

        for sqlorder_info in sqlorder_list:
            try:
                SqlOrder.objects.get_or_create(
                    work_id=sqlorder_info['work_id'],
                    submit_user=sqlorder_info['submit_user'],
                    create_user=sqlorder_info['create_user'],
                    dbinfo=sqlorder_info['dbinfo'],
                    sql=sqlorder_info['sql'],
                    type=sqlorder_info['type'],
                    backup=sqlorder_info['backup'],
                    text=sqlorder_info['text']
                )
                SqlTask.objects.get_or_create(
                    task_id=sqlorder_info['task_id'],
                    sid=sqlorder_info['sid'],
                    svn_path=sqlorder_info['svn_path'],
                    sql_file_path=sqlorder_info['sql_file_path'],
                    sql_file_name=sqlorder_info['sql_file_name'],
                    work_id=sqlorder_info['work_id']
                )
            except Exception as e:
                logger.error(f'{e.__class__.__name__}: {e}')
                return HttpResponse(status=500)

        return Response({'status': 200,
                         'results': [{'task_id': sqlorder_info['task_id'],
                                      'sid': sqlorder_info['sid'],
                                      'work_id': sqlorder_info['work_id']} for sqlorder_info in sqlorder_list]})
