from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    new_password = serializers.CharField()


class GetTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
