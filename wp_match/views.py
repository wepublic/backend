from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from wp_core.models import Answer
from collections import Counter

from django.http import JsonResponse

from users.models import User


@detail_route(methods=['get'], permission_classes=[IsAuthenticated])
def index(request):
    user = User.objects.get(email='admin@wepublic.me')

    answers = Answer.objects.filter(voteanswer__user=user, voteanswer__up=True)
    c = Counter()
    c.update([a.party for a in answers])
    keys = [k.short_name for k in list(c.keys())]
    a = dict(zip(keys, c.values()))
    total = {(k, (v / sum(a.values())) * 100) for k, v in a.items()}

    return JsonResponse([{'content': str(total)}], safe=False)
