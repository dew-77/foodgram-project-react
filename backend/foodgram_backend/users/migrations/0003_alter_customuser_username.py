# Generated by Django 3.2.16 on 2023-12-22 19:37

import django.contrib.auth.validators
from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20231222_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[users.validators.UsernameMeValidator, django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='Юзернейм'),
        ),
    ]
