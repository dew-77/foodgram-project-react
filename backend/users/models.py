from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email as EmailValidator
from django.db import models

from foodgram_backend.constants import (EMAIL_MAX_LENGTH,
                                        FIRST_NAME_MAX_LENGTH,
                                        LAST_NAME_MAX_LENGTH,
                                        PASSWORD_MAX_LENGTH,
                                        USERNAME_MAX_LENGTH)
from .validators import UsernameValidator


class CustomUser(AbstractUser):
    username = models.CharField(
        'Юзернейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[UsernameValidator, UnicodeUsernameValidator()]
    )
    password = models.CharField('Пароль', max_length=PASSWORD_MAX_LENGTH)
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        validators=[EmailValidator],
    )
    first_name = models.CharField('Имя', max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME_MAX_LENGTH)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'password',
        'first_name', 'last_name'
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}'


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    subscribing = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписан'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribing'],
                name='Unique Subscribe'
            )
        ]

    def __str__(self):
        return f'{self.subscriber.username} - {self.subscribing.username}'
