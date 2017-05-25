from rest_framework import serializers
from wp_core.models import *
from users.models import Userprofile
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from wp_core.permissions import IsStaffOrTargetUser


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

    class Meta:
        model = Tag
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):

    upvotes = serializers.SerializerMethodField(
        read_only=True,
    )

    downvotes = serializers.SerializerMethodField(
        read_only=True,
    )


    creator = SmallUserSerializer(
        read_only = True,
    )

    class Meta:
        model = Question
        #fields = '__all__'
        exclude = ('votes',)

    def get_upvotes(self, obj):
        return obj.votes.filter(votequestion__up=True).count()

    def get_downvotes(self, obj):
        return obj.votes.filter(votequestion__up=False).count()

    def create(self, validated_data):
        user =  self.context['request'].user
        question = Question(creator = user, text=validated_data['text'])
        question.save()
        for tag in validated_data['tags']:
            question.tags.add(tag)
        
        return question

    def update(self, instance, validated_data):
        if validated_data.get('tags') is not None:
            instance.tags.clear()
            for tag in validated_data['tags']:
                instance.tags.add(tag)
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

    def validate_text(self, value):
        if Question.objects.filter(text=value).exists():
            raise serializers.ValidationError('Question already exists')
        return value

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
