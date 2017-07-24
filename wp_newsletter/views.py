from rest_framework import viewsets
from rest_framework import mixins

from wp_newsletter.models import NewsLetterAddress
from wp_newsletter.serializers import NewsLetterAddressSerializer
# Create your views here.


class NewsLetterAddressViewSet(mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    queryset = NewsLetterAddress.objects.all()
    serializer_class = NewsLetterAddressSerializer
