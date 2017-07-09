from django.shortcuts import render

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from users.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from wp_news.models import NewsEntry
from wp_news.serializers import NewsEntrySerializer
from wp_news.permissions import ReadOnlyAccess
# Create your views here.


class NewsEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyAccess]
    queryset = NewsEntry.objects.filter(published=True)
    serializer_class = NewsEntrySerializer

