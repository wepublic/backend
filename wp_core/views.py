from django.shortcuts import render

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from wp_core.models import *
from wp_core.serializers import *
from wp_core.permissions import OnlyStaffCanModify, StaffOrOwnerCanModify
from wp_core.pagination import NewestQuestionsSetPagination
# Create your views here.


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [OnlyStaffCanModify]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @detail_route(methods=['get'], pagination_class=NewestQuestionsSetPagination)
    def questions(self, request, pk=None):
        questions = get_object_or_404(Tag,pk=pk).questions
        ser = QuestionSerializer(questions, many=True)
        return Response(ser.data)

class QuestionsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, StaffOrOwnerCanModify]
    queryset = Question.objects.all().order_by('-time_created')
    serializer_class = QuestionSerializer
    pagination_class = NewestQuestionsSetPagination

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        questions = Question.objects.filter(creator=request.user)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        question = get_object_or_404(Question, pk=pk)
        serializer = TagSerializer(question.tags, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def upvote(self, request, pk=None):
        question = get_object_or_404(Question, pk=pk)
        user = request.user
        if VoteQuestion.objects.filter(question=question, user=user, up=False).exists():
            VoteQuestion.objects.get(question=question, user=user, up=False).delete()
        
        if VoteQuestion.objects.filter(question=question, user=user, up=True).exists():
            vote = VoteQuestion.objects.get(question=question, user=user, up=True)
        else:
            vote = VoteQuestion(question=question, user=user, up=True)
            vote.save()
        return Response(self.get_serializer(question).data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def upvotes(self, request):
        user = request.user
        questions = user.votes.all().filter(votequestion__up = True)[::1]
        print(questions)
        return Response(self.get_serializer(questions, many=True).data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def downvotes(self, request):
        user = request.user
        questions = user.votes.all().filter(votequestion__up = False)[::1]
        print(questions)
        return Response(self.get_serializer(questions, many=True).data)



    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def downvote(self, request, pk=None):
        question = get_object_or_404(Question, pk=pk)
        user = request.user
        if VoteQuestion.objects.filter(question=question, user=user, up=True).exists():
            VoteQuestion.objects.get(question=question, user=user, up=True).delete()
        if VoteQuestion.objects.filter(question=question, user=user, up=False).exists():
            vote = VoteQuestion.objects.get(question=question, user=user, up=False)
        else:
            vote = VoteQuestion(question=question, user=user, up=False)
            vote.save()
        return Response(self.get_serializer(question).data, status=status.HTTP_201_CREATED)

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
