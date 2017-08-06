from rest_framework import serializers
from wp_party.models import Party


class PartySerialzier(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = ('id', 'short_name', 'name')
