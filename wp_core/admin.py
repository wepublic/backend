from django.contrib import admin
from wp_core.forms import QuestionForm
from wp_core.models import (
        Question,
        Answer,
        VoteQuestion,
        VoteAnswer,
        Tag
    )

from django.db.models import Sum, When, Case, IntegerField
from django.db.models.functions import Coalesce
import logging
logger = logging.getLogger(__name__)


def close_questions(modeladmin, request, queryset):
    logger.info("closing {} questions...".format(queryset.count()))
    for question in queryset:
        question.close()


close_questions.short_description = "Close the selected Questions for Voting"


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    filter_horizontal = ('tags',)
    actions = [close_questions]
    list_display = (
            'id',
            'text',
            'user',
            'closed',
            'upvotes',
            )

    def get_queryset(self, request):
        qs = super(QuestionAdmin, self).get_queryset(request)
        qs = qs.annotate(
                upvotes=Coalesce(Sum(
                        Case(
                            When(votequestion__up=True, then=1),
                            When(votequestion__up=False, then=0),
                            output_field=IntegerField()
                        )
                    ), 0)
            )
        return qs

    def upvotes(self, obj):
        return obj.upvotes
    upvotes.admin_order_field = 'upvotes'


class VoteQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'question',
    )


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(VoteQuestion, VoteQuestionAdmin)
admin.site.register(VoteAnswer)
admin.site.register(Tag)
