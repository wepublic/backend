from users.models import User
from django.contrib.auth import authenticate
import django.contrib.auth.password_validation as validators
from django.core import exceptions

from rest_framework import serializers
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
                'id',
                'email', 
                'username', 
                'password', 
                'first_name', 
                'last_name', 
                'reputation',
                'profile_pic',
                'zip_code',
                'year_of_birth',
                'gender'
            )
        read_only_fields = (
                'id',
                'reputation',
            )

    def create(self, validated_data):
        created_user = User.objects.create_user(**validated_data)
        return created_user

    def update(self, instance, validated_data):
        user = User.objects.get(id=instance.id)
        user.username = validated_data.get('username', instance.username)
        user.email = validated_data.get('email', instance.email)
        user.first_name = validated_data.get('first_name', instance.first_name)
        user.last_name = validated_data.get('last_name', instance.last_name)
        user.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        user.zip_code = validated_data.get('zip_code', instance.zip_code)
        user.year_of_birth = validated_data.get('year_of_birth', instance.year_of_birth)
        user.gender = validated_data.get('gender', instance.gender)
        user.save()
        return user

    def validate(self, data):
        # here data has all the fields which have validated values
        # so we can create a User instance out of it
        user = User(**data)

        # get the password from the data
        password = data.get('password')

        errors = dict() 
        try:
         # validate the password and catch the exception
         validators.validate_password(password=password, user=User)

        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
         errors['password'] = list(e.messages)

        if errors:
         raise serializers.ValidationError(errors)

        return super(UserSerializer, self).validate(data)

class UserLinkSerializer(serializers.HyperlinkedModelSerializer):   
    class Meta:
        model = User
        fields = ('url','id', 'username', 'profile_pic')
        read_only_fields = ('id','username','profile_pic')

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)


    
