from django.contrib.auth.models import AbstractUser
from django.db import models

from .manager import CustomUserManager

VALID_NAME_VALUES = 150


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    avatar = models.ImageField(
        upload_to='users',
        blank=True,
        verbose_name='Аватар'
    )
    first_name = models.CharField(
        max_length=VALID_NAME_VALUES,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=VALID_NAME_VALUES,
        verbose_name='Фамилия'
    )
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'username', 'last_name', ]

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
