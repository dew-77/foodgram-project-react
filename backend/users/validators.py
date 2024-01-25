from rest_framework import serializers

from foodgram_backend.constants import UNALLOWED_USERNAME


def UsernameValidator(username):
    if username == UNALLOWED_USERNAME:
        raise serializers.ValidationError(
            f'Нельзя использовать юзернейм "{UNALLOWED_USERNAME}".')
    return username
