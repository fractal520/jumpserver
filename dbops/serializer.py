from rest_framework import serializers
from dbops.models.sqlinfo import SqlOrder


class SqlOrderSerializers(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()
    submit_user = serializers.SerializerMethodField()
    dbinfo = serializers.SerializerMethodField()
    exec_user = serializers.SerializerMethodField()

    class Meta:
        model = SqlOrder
        fields = '__all__'


    @staticmethod
    def get_status(obj):
        return obj.status

    @staticmethod
    def get_submit_user(obj):
        return obj.submit_user

    @staticmethod
    def get_submit_user(obj):
        return obj.submit_user

    @staticmethod
    def get_dbinfo(obj):
        return obj.dbinfo.db_name

    @staticmethod
    def get_exec_user(obj):
        return obj.exec_user.name
