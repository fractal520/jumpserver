from rest_framework import serializers
from devops.models import PlayBookTask, AnsibleRole, TaskHistory


class TaskReadSerializer(serializers.ModelSerializer):
    ansible_role_name = serializers.SerializerMethodField()

    class Meta:
        model = PlayBookTask
        exclude = ('_hosts', )

    @staticmethod
    def get_ansible_role_name(obj):
        return obj.ansible_role.name


class TaskSerializer(serializers.ModelSerializer):
    ansible_role_name = serializers.SerializerMethodField()

    # system_user = SystemUserSerializer()

    class Meta:
        model = PlayBookTask
        fields = '__all__'

    @staticmethod
    def get_ansible_role_name(obj):
        return obj.ansible_role.name


class AnsibleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleRole
        fields = '__all__'


class TaskHistorySerializer(serializers.ModelSerializer):
    stat = serializers.SerializerMethodField()
    taskhistory_short_id = serializers.SerializerMethodField()

    class Meta:
        model = TaskHistory
        fields = '__all__'

    @staticmethod
    def get_stat(obj):
        return {
            "total_num": obj.total_num,
            "success_num": obj.success_num,
            "failed_num": obj.failed_num,
        }

    @staticmethod
    def get_taskhistory_short_id(obj):
        return obj.short_id
