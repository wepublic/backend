from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from wp_core.models import Answer
from collections import Counter

from django.http import JsonResponse

from users.models import User
import json


@detail_route(methods=['get'], permission_classes=[IsAuthenticated])
def index(request):
    user = User.objects.get(email='admin@wepublic.me')

    # get the amount of positive voted answers per user
    answers = Answer.objects.filter(voteanswer__user=user, voteanswer__up=True)
    c = Counter()
    c.update([a.party for a in answers])
    keys = [k.short_name for k in list(c.keys())]
    a = dict(zip(keys, c.values()))
    total = [(k, (v / sum(a.values())) * 100) for k, v in a.items()]
    parties = [x[0] for x in total]
    percentage = [x[1] for x in total]

    response = []
    for i, party in enumerate(total):
        d_party = {
            'name': parties[i],
            'percentage': percentage[i]
        }
        response.append(d_party)

    return JsonResponse([{'content': json.dumps(response)}], safe=False)
