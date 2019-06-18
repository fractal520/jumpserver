import pymysql
from django.db.models import Q
from common.utils import get_logger
from dbops.models.sqlinfo import SqlRecord
from dbops.models.inceptioninfo import InceptionInfo

logger = get_logger('jumpserver')


class GenRollBackSql(object):

    def __init__(self, backup_dbname, sequence):
        self.sequence = sequence
        self.backup_dbname = backup_dbname
        self.con = object
        self.inception_info = InceptionInfo.objects.first()

    def __enter__(self):
        self.con = pymysql.connect(host=self.inception_info.back_host,
                                   user=self.inception_info.back_user,
                                   passwd=self.inception_info.back_password,
                                   port=int(self.inception_info.back_port),
                                   db=self.backup_dbname,
                                   charset='utf8')
        return self

    def get_back_table(self):
        with self.con.cursor() as cursor:
            sql = '''
                  select tablename from $_$Inception_backup_information$_$ where opid_time =%s;
                  ''' % self.sequence
            cursor.execute(sql)
            data = cursor.fetchone()
            if data:
                return data[0]

    def get_rollback_sql(self, back_table):
        with self.con.cursor() as cursor:
            sql = '''
                   select rollback_statement,opid_time from %s where opid_time =%s;
                  ''' % (back_table, self.sequence)
            cursor.execute(sql)
            data = cursor.fetchall()
        return data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()
