from django.db import models


class Party(models.Model):
    id = models.SmallAutoField(primary_key=True)
    short_name = models.CharField(
            unique=True,
            max_length=50,
            error_messages={
                'unique': 'A Party with that name already exists'
            }
        )
    name = models.CharField(
            unique=True,
            max_length=200,
            error_messages={
                'unique': 'A Party with that name already exists'
            }
        )

    def __str__(self):
        return self.short_name
