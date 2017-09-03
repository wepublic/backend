from django.core.management.base import BaseCommand
from wp_core.models import Question
from django.db.models import Sum, When, Case, IntegerField
from django.db.models.functions import Coalesce
from users.utils import slack_notify_question
from rest_framework.reverse import reverse_lazy
from django.conf import settings


class Command(BaseCommand):
    help = 'sends the question with the most upvotes to slack'

    def handle(self, *args, **options):
        open_questions = Question.objects.all().filter(closed=False)
        open_questions = open_questions.annotate(
                    upvotes=Coalesce(Sum(
                            Case(
                                When(votequestion__up=True, then=1),
                                When(votequestion__up=False, then=0),
                                output_field=IntegerField()
                            )
                        ), 0)
                )
        question = open_questions.order_by('-upvotes').first()
        path = reverse_lazy(
                'admin:wp_core_question_change',
                args=([question.pk])
                )
        url = "{}{}".format(settings.DOMAIN, path)
        slack_notify_question(question, url)
        print(question.__dict__)
