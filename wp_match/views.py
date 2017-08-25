from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route

from django.http import JsonResponse

from users.models import User


@detail_route(methods=['get'], permission_classes=[IsAuthenticated])
def index(request):

    user = User.objects.get(email='admin@wepublic.me')

    return JsonResponse([ { 'content': str(user) } ], safe=False)
