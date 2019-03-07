from rest_framework import serializers
from .models import PlayBookTask, AnsibleRole


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
        exclude = ('_hosts', )

    @staticmethod
    def get_ansible_role_name(obj):
        return obj.ansible_role.name


class AnsibleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleRole
        fields = '__all__'
