from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import (
        IsAuthenticatedOrReadOnly,
        IsAuthenticated,
    )
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db.models import Sum, When, Case, IntegerField

from random import randint
from wp_core.models import (
        Question,
        Tag,
        VoteQuestion,
    )
from wp_core.serializers import (
        QuestionSerializer,
        TagSerializer,
        AnswerSerializer,
    )
from wp_core.permissions import OnlyStaffCanModify, StaffOrOwnerCanModify
from wp_core.pagination import NewestQuestionsSetPagination


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [OnlyStaffCanModify]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @detail_route(
            methods=['get'],
            pagination_class=NewestQuestionsSetPagination
            )
    def Questions(self, request, pk=None):
        questions = Question.objects.filter(tags__pk=pk).annotate(
                upvotes=Sum(
                        Case(
                            When(votequestion__up=True, then=1),
                            output_field=IntegerField()
                        )
                    )
            )
        ser = QuestionSerializer(
                questions,
                many=True,
                context={'request': request}
            )
        return Response(ser.data)


class QuestionsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, StaffOrOwnerCanModify]
    queryset = Question.objects.annotate(
                upvotes=Sum(
                        Case(
                            When(votequestion__up=True, then=1),
                            output_field=IntegerField()
                        )
                    )
            )
    serializer_class = QuestionSerializer
    pagination_class = NewestQuestionsSetPagination
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('time_created', 'upvotes')
    ordering = ('-time_created')

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        questions = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def answers(self, request, pk=None):
        try:
            question = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(
                    detail='Question with the id %s does not exist' % pk
                )
        return Response(
                AnswerSerializer(
                    question.answers.all(),
                    many=True,
                    context={'request': request}
                ).data
            )

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):

        try:
            question = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(
                    detail='Question with the id %s does not exist' % pk
                )

        serializer = TagSerializer(question.tags, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def random(self, request):
        questions = self.get_queryset().exclude(
                votequestion__user=request.user
                ).filter(answers=None)
        questions_length = questions.count()
        if questions_length == 0:
            return Response({"detail": "No Questions Left"}, status=429)
        if questions_length == 1:
            return Response(
                    self.get_serializer(
                        questions[0]
                        ).data
                   )

        return Response(
                self.get_serializer(
                    questions[randint(0, questions_length-1)]
                ).data
            )

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def upvote(self, request, pk=None):
        try:
            question = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(
                    detail='Question with the id %s does not exist' % pk
                )
        user = request.user
        if VoteQuestion.objects.filter(
                question=question, user=user, up=False
        ).exists():
            VoteQuestion.objects.get(
                    question=question,
                    user=user,
                    up=False
                ).delete()
        if VoteQuestion.objects.filter(
                question=question, user=user, up=True
        ).exists():
            vote = VoteQuestion.objects.get(
                    question=question,
                    user=user,
                    up=True
                )
        else:
            vote = VoteQuestion(question=question, user=user, up=True)
            vote.save()
        question = self.get_queryset().get(pk=pk)
        return Response(self.get_serializer(question).data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def upvotes(self, request):
        user = request.user
        questions = self.get_queryset().filter(
                votequestion__up=True,
                votequestion__user=user
            )
        questions = filters.OrderingFilter().filter_queryset(
                self.request,
                questions,
                self
            )
        return Response(self.get_serializer(questions, many=True).data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def downvotes(self, request):
        user = request.user
        questions = self.get_queryset().filter(
                votequestion__up=False,
                votequestion__user=user
            )
        return Response(self.get_serializer(questions, many=True).data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def downvote(self, request, pk=None):
        try:
            question = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(detail='Question id %s does not exist' % pk)
        user = request.user
        try:
            VoteQuestion.objects.get(
                    question=question,
                    user=user,
                    up=True
                ).delete()
        except VoteQuestion.DoesNotExist:
            pass
        try:
            vote = VoteQuestion.objects.get(
                    question=question,
                    user=user,
                    up=False
                )
        except VoteQuestion.DoesNotExist:
            vote = None
        if vote is None:
            vote = VoteQuestion(question=question, user=user, up=False)
            vote.save()

        question = self.get_queryset().get(pk=pk)
        return Response(
                self.get_serializer(question).data,
                status=status.HTTP_201_CREATED
            )
