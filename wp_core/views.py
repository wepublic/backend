from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import (
        IsAuthenticatedOrReadOnly,
        IsAuthenticated,
    )
from rest_framework.reverse import reverse_lazy
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.throttling import UserRateThrottle

from django.db.models import Sum, When, Case, IntegerField, BooleanField, Value
from django.db.models.functions import Coalesce
from users.utils import slack_notify_report

from random import randint

from wepublic_backend.settings import NOREPLY_ADDRESS
from wp_core.models import (
    Question,
    Tag, VoteQuestion,
)
from wp_core.serializers import (
        QuestionSerializer,
        TagSerializer,
        AnswerSerializer,
        VoteQuestionSerializer,
    )
from wp_core.permissions import OnlyStaffCanModify, StaffOrOwnerCanModify
from wp_core.pagination import NewestQuestionsSetPagination

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from django.core.serializers.json import DjangoJSONEncoder


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [OnlyStaffCanModify]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(detail=True,
            methods=['get'],
            pagination_class=NewestQuestionsSetPagination,
            throttle_classes=[UserRateThrottle]
            )
    def Questions(self, request, pk=None):
        questions = Question.objects.filter(tags__pk=pk).annotate(
                upvotes=Coalesce(Sum(
                        Case(
                            When(votequestion__up=True, then=1),
                            When(votequestion__up=False, then=0),
                            output_field=IntegerField()
                        )
                    ), 0)
            )
        ser = QuestionSerializer(
                questions,
                many=True,
                context={'request': request}
            )
        return Response(ser.data)


class QuestionsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, StaffOrOwnerCanModify]
    serializer_class = QuestionSerializer
    pagination_class = NewestQuestionsSetPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    search_fields = ['text']
    ordering_fields = ('time_created', 'upvotes', 'closed_date')
    ordering = ('-time_created')

    def get_queryset(self):
        request = self.request
        qs = self.get_annotated_questions()
        if 'answered' in request.GET and request.GET['answered'] is not None:
            answered = request.GET['answered']
            if answered == 'true':
                return qs.exclude(answers=None)
            if answered == 'false':
                return qs.filter(answers=None)

        return qs

    def get_annotated_questions(self):
        qs = Question.objects.annotate(
                    upvotes=Coalesce(Sum(
                            Case(
                                When(votequestion__up=True, then=1),
                                When(votequestion__up=False, then=0),
                                output_field=IntegerField()
                            )
                        ), 0)
                )
        return qs

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.update_reputation('CREATE_QUESTION'):
            return Response({"detail": "Not enough reputation"}, status=420)

        question = serializer.save()
        # self.perform_create(serializer)
        question.vote_by(request.user, True, update_rep=False)
        headers = self.get_success_headers(serializer.data)
        return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def my(self, request):
        """Gets all own and voted for questions."""
        questions = self.get_queryset().filter(user=request.user).annotate(own=Value(True))
        serializer = self.get_serializer(questions, many=True)
        data = serializer.data

        voted_questions = VoteQuestion.objects.filter(Q(user=request.user), Q(up=True))
        for item in voted_questions:
            real_question = self.get_queryset().get(pk=item.question.id)
            serialized_voted_question = self.get_serializer(real_question, many=False).data
            serialized_voted_question['own'] = False
            if request.user != real_question.user:
                data.append(serialized_voted_question)

        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def answers(self, request, pk=None) -> HttpResponse:
        try:
            question = Question.objects.all().get(pk=pk)
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

    @action(detail=True, methods=['get'])
    def tags(self, request, pk=None) -> HttpResponse:

        try:
            question = Question.objects.all().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(
                    detail='Question with the id %s does not exist' % pk
                )

        serializer = TagSerializer(question.tags, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], throttle_classes=[UserRateThrottle])
    def random(self, request) -> HttpResponse:
        if (request.user.is_anonymous is True):
            questions = self.get_annotated_questions().filter(
                closed=False
                )
            return Response(
                self.get_serializer(
                    questions[randint(0, questions.count()-1)]
                ).data
            )
        questions = self.get_annotated_questions().filter(
                closed=False
                ).exclude(
                votequestion__user=request.user
                )
        questions_length = questions.count()
        if questions_length == 0:
            return Response({"detail": "No Questions Left"}, status=204)
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def upvote(self, request, pk=None) -> HttpResponse:
        try:
            question = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(
                    detail='Question with the id %s does not exist' % pk
                )

        if question.closed:
            raise PermissionDenied(
                    detail='Question {} is already closed'.format(question.id))
        question.vote_by(request.user, True)

        # get the question again, so the upvote count updates
        question = self.get_queryset().get(pk=pk)
        return Response(self.get_serializer(question).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def myvotes(self, request) -> HttpResponse:
        user = request.user

        votes = VoteQuestion.objects.filter(user=user)

        return Response(VoteQuestionSerializer(votes, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def upvotes(self, request) -> HttpResponse:
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
        answered = request.GET.get('answered')

        if answered is not None:
            if answered == 'true':
                questions = questions.exclude(answers=None)
            if answered == 'false':
                questions = questions.filter(answers=None)

        return Response(self.get_serializer(questions, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def downvotes(self, request) -> HttpResponse:
        user = request.user
        questions = self.get_queryset().filter(
                votequestion__up=False,
                votequestion__user=user
            )
        return Response(self.get_serializer(questions, many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def downvote(self, request, pk=None) -> HttpResponse:
        try:
            question = self.get_queryset().get(pk=pk)
        except Question.DoesNotExist:
            raise NotFound(detail='Question id %s does not exist' % pk)
        if question.closed:
            raise PermissionDenied(
                    detail='Question {} is already closed'.format(question.id))
        question.vote_by(request.user, False)
        question = self.get_queryset().get(pk=pk)
        return Response(
                self.get_serializer(question).data,
                status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], throttle_classes=[UserRateThrottle])
    def report(self, request, pk=None) -> HttpResponse:
        user = request.user
        url = reverse_lazy(
                'admin:wp_core_question_change',
                args=([pk]),
                request=request
                )
        question = self.get_object()
        reason = request.data.get('reason', 'nichts angegeben')
        params = {
                'question': question.text,
                'link': url,
                'reason': reason,
                'reporter': user,
                }
        plain = render_to_string(
                'wp_core/mails/report_question_email.txt', params)
        html = render_to_string(
                'wp_core/mails/report_question_email.html', params)
        if settings.REPORT_MAILS_ACTIVE:
            emails = settings.REPORT_MAILS

            send_mail(
                    'Eine Frage wurde gemeldet',
                    plain,
                    NOREPLY_ADDRESS,
                    emails,
                    html_message=html
            )
        slack_notify_report(question.text, reason, url, user)
        return Response({'success': True})
