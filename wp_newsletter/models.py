from django.db import models


class NewsLetterAddress(models.Model):
    email = models.EmailField(
            'email address',
            unique=True,
    )
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.email)
