from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateMixin
from rest_framework import serializers

from foodgram_backend.constants import PASSWORD_MAX_LENGTH
from recipes.models import Recipe
from .models import Subscribe

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            subscriber=user, subscribing=obj).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )
        read_only_fields = fields


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserRecipeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.carts.filter(user=user).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeSubscribeSerializer(recipes, many=True, context={
            'request': self.context['request']
        }).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def validate(self, data):
        user = self.context['request'].user
        sub_candidate = self.instance
        if user == sub_candidate:
            raise serializers.ValidationError(
                {'errors': 'You cannot subscribe to yourself.'})

        if user.subscriber.filter(subscribing_id=sub_candidate.id).exists():
            raise serializers.ValidationError(
                {"errors": "Already subscribed."})

        return data

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'recipes', 'recipes_count',
            'is_subscribed'
        )
        read_only_fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )


class CreateUserSerializer(UserCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, max_length=PASSWORD_MAX_LENGTH,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )
        read_only_fields = ('id',)
