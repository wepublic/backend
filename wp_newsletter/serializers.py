from wp_newsletter.models import NewsLetterAddress
from rest_framework import serializers


class NewsLetterAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsLetterAddress
        fields = (
                'id',
                'email',
                'time_created'
        )
        read_only_fields = (
                'id',
                'time_created'
        )
