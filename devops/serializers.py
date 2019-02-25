# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals

from rest_framework import serializers

from .models import *
from assets.serializers import *
from assets.models import *


class AnsibleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleRole
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    ansible_role_name = serializers.SerializerMethodField()
    tags = serializers.ListField(required=False, child=serializers.CharField())

    # system_user = SystemUserSerializer()

    class Meta:
        model = PlayBookTask
        exclude = ('assets', 'groups')

    @staticmethod
    def get_ansible_role_name(obj):
        return obj.ansible_role.name


class TaskReadSerializer(serializers.ModelSerializer):
    ansible_role_name = serializers.SerializerMethodField()
    is_success = serializers.SerializerMethodField()
    tags = serializers.ListField(required=False, child=serializers.CharField())

    class Meta:
        model = PlayBookTask
        exclude = ('assets', 'groups', 'password',)

    @staticmethod
    def get_ansible_role_name(obj):
        return obj.ansible_role.name

    @staticmethod
    def get_is_success(obj):
        return  obj.latest_history.is_success if obj.latest_history else None


class TaskUpdateGroupSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Node.objects.all())

    class Meta:
        model = PlayBookTask
        fields = ['id', 'groups']


class TaskUpdateAssetSerializer(serializers.ModelSerializer):
    assets = serializers.PrimaryKeyRelatedField(many=True, queryset=Asset.objects.all())

    class Meta:
        model = PlayBookTask
        fields = ['id', 'assets']


class TaskUpdateSystemUserSerializer(serializers.ModelSerializer):
    system_user = serializers.PrimaryKeyRelatedField(many=False, queryset=SystemUser.objects.all(), allow_null=True)

    class Meta:
        model = PlayBookTask
        fields = ['id', 'system_user']


class VariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        exclude = ('assets', 'groups')


class VariableVarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = ('id',)


class VariableUpdateGroupSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Node.objects.all())

    class Meta:
        model = Variable
        fields = ['id', 'groups']


class VariableUpdateAssetSerializer(serializers.ModelSerializer):
    assets = serializers.PrimaryKeyRelatedField(many=True, queryset=Asset.objects.all())

    class Meta:
        model = Variable
        fields = ['id', 'assets']


class TaskWebhookSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=200)

    class Meta:
        model = PlayBookTask
        fields = ['password']
