from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

VALID_NAME_VALUES = 128


class TagIngredient(models.Model):
    name = models.CharField(
        max_length=VALID_NAME_VALUES,
        verbose_name='Название'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.name)
