from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email as EmailValidator
from .validators import UsernameMeValidator


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)

    username = models.CharField(
        'Юзернейм',
        max_length=150,
        unique=True,
        validators=[UsernameMeValidator, UnicodeUsernameValidator()]
    )
    password = models.CharField('Пароль', max_length=150)
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        validators=[EmailValidator],
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

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
        related_name='subscriber'
        )
    subscribing = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        unique_together = ('subscriber', 'subscribing')

    def __str__(self):
        return f'{self.subscriber} to {self.subscribing}'
