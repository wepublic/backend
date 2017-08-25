from rest_framework import viewsets

from django.http import JsonResponse


def index(request):

    

    return JsonResponse([ { 'content': 'asdf' } ], safe=False)
