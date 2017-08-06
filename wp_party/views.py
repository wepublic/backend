from rest_framework import viewsets
from rest_framework import mixins

from wp_party.models import Party
from wp_party.serializers import PartySerialzier


class PartyViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = PartySerialzier
    queryset = Party.objects.all()
