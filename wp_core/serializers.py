from rest_framework import serializers
from wp_core.models import *
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from wp_core.permissions import IsStaffOrTargetUser
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password','username' ,'first_name', 'last_name', 'email',)
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)
 
     
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def get_permissions(self):
        if self.request.method == 'POST':
            return AllowAny()
        else: 
            return IsStaffOrTargetUser()



class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        

class UserLinkSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url','username')

        

class SmallQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text')

class SmallTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id','text')

class TagSerializer(serializers.ModelSerializer):
    questions = SmallQuestionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Tag
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    tags = SmallTagSerializer (
        many = True,
    )
    votes = serializers.SerializerMethodField(
        read_only=True,
    )

    creator = SmallUserSerializer(
        read_only = True,
    )

    class Meta:
        model = Question
        fields = '__all__'

    def get_votes(self, obj):
        return obj.votes.count()


class UserprofileSerializer(serializers.HyperlinkedModelSerializer):
    user = SmallUserSerializer()
    class Meta:
        model = Userprofile
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
    )
    question = serializers.PrimaryKeyRelatedField(
        queryset = Question.objects.all()
    )
    class Meta:
        model = Answer
        fields = "__all__"
