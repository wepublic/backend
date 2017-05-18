from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.authtoken.models import Token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


