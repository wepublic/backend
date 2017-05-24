from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from users.models import Userprofile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)
    first_name= serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    reputation = serializers.IntegerField(source="userprofile.reputation", read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'reputation')

    def create(self, validated_data):
        created_user = User.objects.create_user(**validated_data)
        return created_user

    def update(self, instance, validated_data):
        user = User.objects.get(id=instance.id)
        user.username = validated_data.get('username', instance.username)
        user.email = validated_data.get('email', instance.email)
        user.first_name = validated_data.get('first_name', instance.first_name)
        user.last_name = validated_data.get('last_name', instance.last_name)
        user.save()
        return user

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)


    
