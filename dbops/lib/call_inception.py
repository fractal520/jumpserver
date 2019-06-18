import pymysql
from ..models.inceptioninfo import InceptionInfo
from common.utils import get_logger


logger = get_logger('jumpserver')
pymysql.install_as_MySQLdb()


class Inception(object):
    def __init__(self, LoginDic=None):
        self.__dict__.update(LoginDic)
        self.con = object

    def __enter__(self):
        inception_info = InceptionInfo.objects.first()
        port = int(inception_info.port)
        self.con = pymysql.connect(host=inception_info.host,
                                   user=inception_info.user,
                                   passwd=inception_info.password,
                                   port=port,
                                   db='',
                                   charset='utf8')
        return self

    def GenerateStatements(self, Sql: str = '', Type: str = '', backup=None):
        if Sql[-1] == ';':
            Sql = Sql.rstrip(';')
        elif Sql[-1] == '；':
            Sql = Sql.rstrip('；')
        if backup is not None and backup != 0:
            InceptionSQL = '''
             /*--user={user};--password={password};--host={host};--port={port};{Type};{backup};*/ \
             inception_magic_start;\
             use `{db}`;\
             {Sql}; \
             inception_magic_commit;
            '''.format(user=self.__dict__.get('user'),
                       password=self.__dict__.get('password'),
                       host=self.__dict__.get('host'),
                       port=self.__dict__.get('port'),
                       Type=Type,
                       backup=backup,
                       db=self.__dict__.get('db'),
                       Sql=Sql)
            return InceptionSQL
        else:
            InceptionSQL = '''
             /*--user={user};--password={password};--host={host};--port={port};{Type};*/ \
             inception_magic_start;\
             use `{db}`;\
             {Sql}; \
             inception_magic_commit;
            '''.format(user=self.__dict__.get('user'),
                       password=self.__dict__.get('password'),
                       host=self.__dict__.get('host'),
                       port=self.__dict__.get('port'),
                       Type=Type,
                       db=self.__dict__.get('db'),
                       Sql=Sql)
            return InceptionSQL

    def Execute(self, sql, backup: int):
        if backup == 1:
            Inceptionsql = self.GenerateStatements(Sql=sql, Type='--enable-execute')
        else:
            Inceptionsql = self.GenerateStatements(
                Sql=sql,
                Type='--enable-execute',
                backup='--disable-remote-backup')
        with self.con.cursor() as cursor:
            cursor.execute(Inceptionsql)
            result = cursor.fetchall()
            Dataset = [
                {
                    'ID': row[0],
                    'stage': row[1],
                    'errlevel': row[2],
                    'stagestatus': row[3],
                    'errormessage': row[4],
                    'sql': row[5],
                    'affected_rows': row[6],
                    'sequence': row[7],
                    'backup_dbname': row[8],
                    'execute_time': row[9],
                    'SQLSHA1': row[10]
                }
                for row in result
            ]
        return Dataset

    def Check(self, sql=None):
        Inceptionsql = self.GenerateStatements(Sql=sql, Type='--enable-check')
        with self.con.cursor() as cursor:
            cursor.execute(Inceptionsql)
            result = cursor.fetchall()
            Dataset = [
                {
                    'ID': row[0],
                    'stage': row[1],
                    'errlevel': row[2],
                    'stagestatus': row[3],
                    'errormessage': row[4],
                    'sql': row[5],
                    'affected_rows': row[6],
                    'SQLSHA1': row[10]
                }
                for row in result
            ]
        return Dataset

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def __str__(self):
        return '''

        InceptionSQL Class

        '''
