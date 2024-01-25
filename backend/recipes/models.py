from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from colorfield.fields import ColorField

from foodgram_backend.constants import (
    TAG_NAME_MAX_LENGTH, TAG_DEFAULT_COLOR, TAG_SLUG_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH, UNIT_NAME_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH, IMAGE_UPLOAD_PATH,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=TAG_NAME_MAX_LENGTH)
    color = ColorField('Цвет', default=TAG_DEFAULT_COLOR)
    slug = models.SlugField(
        'Слаг', max_length=TAG_SLUG_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=INGREDIENT_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=UNIT_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='Unique Ingredient (name with unit)'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField('Изображение', upload_to=IMAGE_UPLOAD_PATH)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(1, message='Cooking time cannot be less than 1.')
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Кол-во ингредиентов (связующая таблица)'
        verbose_name_plural = 'кол-во ингредиентов'
        ordering = ['recipe__name']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Unique IngredientRecipe'
            )
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient.name} для {self.recipe.name}'


class BaseUserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)ss'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)ss'
    )

    class Meta:
        abstract = True
        unique_together = ['user', 'recipe']


class Cart(BaseUserRecipe):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return f'Cart of {self.user.username} for {self.recipe}'


class Favorite(BaseUserRecipe):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'

    def __str__(self):
        return f'"{self.recipe}" / {self.user.username}'
