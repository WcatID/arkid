from tenant.models import Tenant
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from drf_spectacular.utils import extend_schema_field
from .tenant import TenantSerializer


class TSerializer(serializers.Serializer):

    token = serializers.CharField(read_only=True)
    tenants = serializers.ListField(child=TenantSerializer())

    class Meta:

        fields = (
            'token',
        )


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    error = serializers.CharField(read_only=True)
    data = TSerializer(read_only=True)

    class Meta:

        fields = (
            'username',
            'password',
        )