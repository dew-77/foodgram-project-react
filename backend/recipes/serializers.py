from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import Recipe, Ingredient, Tag, RecipeIngredient
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='ingredienttorecipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.carts.filter(user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)

    def validate_tags(self, tags):
        tags_list = []
        if not tags:
            raise serializers.ValidationError('Tags are required for recipe.')
        for tag in tags:
            if tag.id in tags_list:
                raise serializers.ValidationError(
                    'Tags must be unique.')
            tags_list.append(tag.id)
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError('Tag does not exist.')
        return tags

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Ingredients are not provided.')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ingredients must be unique.')
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Amount cannot be less than 1.')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Cooking time must be bigger than 1 minute.')
        return cooking_time

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Image field cannot be empty.')
        return image

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            ingredient_list.append(
                RecipeIngredient(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe,
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' not in validated_data:
            raise serializers.ValidationError({
                'tags': 'This field is required for updating.'
            })

        if 'ingredients' not in validated_data:
            raise serializers.ValidationError({
                'ingredients': 'This field is required for updating.'
            })

        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))

        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)
