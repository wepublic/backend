from rest_framework import serializers
from wp_core.models import (
        Question,
        Answer,
        Tag,
        VoteAnswer,
        VoteQuestion,
    )
from users.models import User
from wp_party.models import Party
from wp_party.serializers import PartySerialzier
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


class VoteQuestionSerializer(serializers.ModelSerializer):
    up = serializers.BooleanField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VoteQuestion
        fields = ('question', 'up')


class QuestionSerializer(serializers.ModelSerializer):
    upvotes = serializers.IntegerField(read_only=True)
    voted = serializers.SerializerMethodField(read_only=True)
    answers = AnswerLinkSerializer(many=True, read_only=True)
    own = serializers.SerializerMethodField()

    class Meta:
        model = Question
        exclude = ('votes', 'user')

    def get_own(self, obj):
        try:
            return obj.user == self.context['request'].user
        except:
            return None

    def get_voted(self, obj):
        if ('request' in self.context and
                self.context['request'].user is not None and
                self.context['request'].user in obj.votes.all()):
            return VoteQuestion.objects.get(
                    question=obj,
                    user=self.context['request'].user
                    ).up
        else:
            return None

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

    def validate_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError('Only 3 Tags are allowed')
        return value


class QuestionLinkSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Question
        fields = ('url', 'text', 'id')


class AnswerSerializer(serializers.ModelSerializer):
    user = UserLinkSerializer()
    question = QuestionLinkSerializer(read_only=True)
    party = PartySerialzier(read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    voted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        exclude = ('votes',)

    def get_voted(self, obj):
        if ('request' in self.context and
                self.context['request'].user is not None and
                self.context['request'].user in obj.votes.all()):
            return VoteAnswer.objects.get(answer=obj,
                                          user=self.context['request'].user).up
        else:
            return None


class AnswerPostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question = serializers.PrimaryKeyRelatedField(
            queryset=Question.objects.all()
        )
    party = serializers.PrimaryKeyRelatedField(
            queryset=Party.objects.all()
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
