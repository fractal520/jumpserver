# encoding: utf-8

from rest_framework import serializers

from deploy.models import DeployRecord, Project


class DeployHistorySerializer(serializers.ModelSerializer):
    asset = serializers.SerializerMethodField()
    app_name = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    deploy_user = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    record_type = serializers.SerializerMethodField()

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

    @staticmethod
    def get_deploy_user(obj):
        try:
            return obj.deploy_user.name
        except AttributeError as error:
            return None

    @staticmethod
    def get_history(obj):
        try:
            return obj.history.id
        except AttributeError as error:
            return None

    @staticmethod
    def get_record_type(obj):
        return obj.get_record_type_display()


class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class ProjectCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['name', 'desc', 'created_by']
