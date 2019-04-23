# encoding: utf-8

from rest_framework import serializers

from deploy.models import DeployRecord


class DeployHistorySerializer(serializers.ModelSerializer):
    asset = serializers.SerializerMethodField()
    app_name = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()

    class Meta:
        model = DeployRecord
        fields = '__all__'

    @staticmethod
    def get_asset(obj):
        return "{}({})".format(obj.asset.hostname, obj.asset.ip)

    @staticmethod
    def get_app_name(obj):
        return obj.app_name.app_name

    @staticmethod
    def get_version(obj):
        return obj.version.version
