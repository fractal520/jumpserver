import threading
import traceback
from django.utils import timezone
from common.utils import get_logger
from dbops.lib import call_inception
from dbops.models.sqlinfo import SqlOrder, SqlRecord

logger = get_logger('jumpserver')


class ExecSql(threading.Thread):

    def __init__(self, work_id, exec_user):
        super().__init__()
        self.exec_user = exec_user
        self.work_id = work_id
        self.sqlorder = SqlOrder.objects.filter(work_id=work_id).first()

    def run(self):
        self.execute()

    def execute(self):
        db = self.sqlorder.dbinfo
        sql = self.sqlorder.sql
        backup = self.sqlorder.backup
        try:
            with call_inception.Inception(
                    LoginDic={
                        'host': db.ip,
                        'user': db.username,
                        'password': db.password,
                        'db': db.db_name,
                        'port': db.port
                    }
            ) as f:
                res = f.Execute(sql=sql, backup=backup)
                for i in res:
                    if i['errlevel'] != 0:
                        SqlOrder.objects.filter(work_id=self.work_id).update(status=4)
                    SqlRecord.objects.get_or_create(
                        work_id=self.work_id,
                        state=i['stagestatus'],
                        sql=i['sql'],
                        sequence=i['sequence'],
                        error=i['errormessage'],
                        affectrow=i['affected_rows'],
                        execute_time=i['execute_time'],
                        backup_dbname=i['backup_dbname'],
                        sqlsha1=i['SQLSHA1'],
                    )
        except Exception as e:
            logger.error(f'{e.__class__.__name__}--sql执行失败: {e}')
            traceback.print_exc()
        finally:
            exec_time = timezone.now()
            SqlOrder.objects.filter(work_id=self.work_id).update(exec_time=exec_time)
            SqlOrder.objects.filter(work_id=self.work_id).update(exec_user=self.exec_user)
            status = SqlOrder.objects.filter(work_id=self.work_id).first()
            if status.status != 4:
                SqlOrder.objects.filter(work_id=self.work_id).update(status=3)

