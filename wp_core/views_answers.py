from rest_framework import viewsets
from rest_framework.permissions import (
        IsAuthenticatedOrReadOnly,
        IsAuthenticated,
    )
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db.models import Sum, When, Case, IntegerField
from django.db.models.functions import Coalesce

from wp_core.models import Answer, VoteAnswer, Question
from wp_core.serializers import AnswerSerializer, AnswerPostSerializer
from wp_core.permissions import OnlyStaffAndPoliticianCanModify


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [
            IsAuthenticatedOrReadOnly,
            OnlyStaffAndPoliticianCanModify
        ]
    queryset = Answer.objects.annotate(
                upvotes=Coalesce(Sum(
                    Case(
                        When(voteanswer__up=True, then=1),
                        When(voteanswer__up=False, then=0),
                        output_field=IntegerField()
                    )
                ), 0)
            )
    serializer_class = AnswerSerializer

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'create' or self.action == 'update':
            return AnswerPostSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upvote(self, request, pk=None):
        try:
            answer = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(detail='Answer with the id %s does not exist' % pk)
        VoteAnswer.objects.update_or_create(
                answer=answer,
                user=request.user,
                defaults={
                        'up': True
                    }
                )
        return Response(self.get_serializer(answer).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def downvote(self, request, pk=None):
        try:
            answer = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(detail='Answer with the id %s does not exist' % pk)
        VoteAnswer.objects.update_or_create(
                answer=answer,
                user=request.user,
                defaults={
                    'up': False
                }
        )
        return Response(self.get_serializer(answer).data)
