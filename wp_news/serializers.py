from wp_news.models import NewsEntry
from users.models import User
from rest_framework import serializers


class NewsUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
                'id',
                'username',
                'profile_pic',
            )


class NewsEntrySerializer(serializers.ModelSerializer):
    user = NewsUserSerializer(read_only=True)

    class Meta:
        model = NewsEntry
        fields = (
                'id',
                'title',
                'content',
                'time_created',
                'last_modified',
                'user',
            )
        read_only_fields = (
                'id',
                'time_created',
                'last_modified',
                )
