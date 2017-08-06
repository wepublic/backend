from django import forms
from django.core.exceptions import ValidationError
from wp_core.models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def clean(self):
        tags = self.cleaned_data.get('tags')
        if tags and tags.count() > 3:
            raise ValidationError('Only three Tags allowed')

        return self.cleaned_data
