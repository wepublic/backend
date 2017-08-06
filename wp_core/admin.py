from django.contrib import admin
from wp_core.forms import QuestionForm
from wp_core.models import (
        Question,
        Answer,
        VoteQuestion,
        VoteAnswer,
        Tag
    )


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    filter_horizontal = ('tags',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(VoteQuestion)
admin.site.register(VoteAnswer)
admin.site.register(Tag)
