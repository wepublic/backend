from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import (
        IsAuthenticatedOrReadOnly,
        IsAuthenticated,
    )
from rest_framework.reverse import reverse_lazy
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

from django.db.models import Sum, When, Case, IntegerField
from users.utils import slack_notify_report

from random import randint
from wp_core.models import (
        Question,
        Tag,
    )
from wp_core.serializers import (
        QuestionSerializer,
        TagSerializer,
        AnswerSerializer,
    )
from wp_core.permissions import OnlyStaffCanModify, StaffOrOwnerCanModify
from wp_core.pagination import NewestQuestionsSetPagination

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


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
                            When(votequestion__up=False, then=0),
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

        if not request.user.update_reputation('CREATE_QUESTION'):
            raise PermissionDenied(detail='Not Enough Reputation')

        question = serializer.save()
        # self.perform_create(serializer)
        question.vote_by(request.user, True, update_rep=False)
        headers = self.get_success_headers(serializer.data)
        return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        questions = self.get_queryset().filter(user=request.user)
        answered = request.GET.get('answered')
        if answered is not None:
            if answered == 'true':
                questions = questions.exclude(answers=None)
            if answered == 'false':
                questions = questions.filter(answers=None)
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

        question.vote_by(request.user, True)

        # get the question again, so the upvote count updates
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
        answered = request.GET.get('answered')

        if answered is not None:
            if answered == 'true':
                questions = questions.exclude(answers=None)
            if answered == 'false':
                questions = questions.filter(answers=None)

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
        question.vote_by(request.user, False)
        question = self.get_queryset().get(pk=pk)
        return Response(
                self.get_serializer(question).data,
                status=status.HTTP_201_CREATED
            )

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        user = request.user
        emails = settings.REPORT_MAILS
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
            send_mail(
                    'Eine Frage wurde gemeldet',
                    plain,
                    'admin@wepublic.me',
                    emails,
                    html_message=html
            )
        slack_notify_report(question.text, reason, url, user)
        return Response({'success': True})
