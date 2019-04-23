# encoding: utf-8

from rest_framework import serializers

from deploy.models import DeployRecord


class DeployHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = DeployRecord
        fields = '__all__'
