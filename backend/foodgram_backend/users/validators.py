from rest_framework import serializers


def UsernameMeValidator(username):
    if username == 'me':
        raise serializers.ValidationError('Нельзя использовать юзернейм "me".')
    return username
