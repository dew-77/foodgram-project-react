from django.contrib import admin
from django.utils.html import format_html

from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'display_image_preview', 'display_author_data',
        'display_favorite_count'
    )

    list_filter = ('author', 'tags__name')

    search_fields = ('name',)

    inlines = [RecipeIngredientInline]

    def display_author_data(self, obj):
        return f'{obj.author.first_name} {obj.author.last_name}'

    def display_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def display_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" />', obj.image.url
            )
        return 'No Image'

    display_author_data.short_description = 'Автор'
    display_favorite_count.short_description = 'В избранном'
    display_image_preview.short_description = 'Превью изображения'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )

    list_filter = ('measurement_unit',)

    search_fields = ('name',)


admin.site.register(RecipeIngredient)
admin.site.register(Tag)
admin.site.register(Cart)
admin.site.register(Favorite)
