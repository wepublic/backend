from django import forms
from users.models import User
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from django.utils import timezone


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
            label="Neues Passwort",
            max_length=100,
            widget=forms.PasswordInput()
            )
    new_password_confirm = forms.CharField(
            label="Bestätige das Passwort",
            max_length=100,
            widget=forms.PasswordInput()
            )
    key = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        key = cleaned_data.get("key")
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")
        try:
            user = User.objects.get(reset_password_key=key)
        except User.DoesNotExist:
            self.add_error('new_password', 'something went wrong')
            return
        if new_password != new_password_confirm:
            msg = "Die Passwörter müssen übereinstimmen!"
            self.add_error('new_password', msg)
            self.add_error('new_password_confirm', msg)
        try:
            validators.validate_password(new_password, user)
        except ValidationError as e:
            self.add_error('new_password', e)
            print(e)

        if timezone.now() > user.reset_password_key_expires:
            self.add_error('new_password', 'Link abgelaufen')
