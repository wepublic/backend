from rest_framework import serializers
from wp_core.models import (
        Question,
        Answer,
        Tag,
    )
from users.models import User
from users.serializers import UserLinkSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class AnswerLinkSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = ('id', 'user')


class QuestionSerializer(serializers.ModelSerializer):
    upvotes = serializers.IntegerField(read_only=True)
    voted = serializers.SerializerMethodField(read_only=True)
    answers = AnswerLinkSerializer(many=True, read_only=True)
    user = UserLinkSerializer(read_only=True)

    class Meta:
        model = Question
        exclude = ('votes',)

    def get_voted(self, obj):
        if ('request' in self.context and
                self.context['request'].user is not None):
            return self.context['request'].user in obj.votes.all()
        else:
            return False

    def create(self, validated_data):
        user = self.context['request'].user
        question = Question(user=user, text=validated_data['text'])
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


class QuestionLinkSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Question
        fields = ('url', 'text', 'id')


class AnswerSerializer(serializers.ModelSerializer):
    user = UserLinkSerializer()
    question = QuestionLinkSerializer(read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    voted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        exclude = ('votes',)

    def get_voted(self, obj):
        if ('request' in self.context and
                self.context['request'].user is not None):
            return self.context['request'].user in obj.votes.all()
        else:
            return False


class AnswerPostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question = serializers.PrimaryKeyRelatedField(
            queryset=Question.objects.all()
        )
    upvotes = serializers.IntegerField(read_only=True)
    voted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = "__all__"

    def get_voted(self, obj):
        if ('request' in self.context and
                self.context['request'].user is not None):
            return self.context['request'].user in obj.votes.all()
        else:
            return False
