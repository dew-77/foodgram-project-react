from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscribe


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'is_superuser', 'first_name', 'last_name',
        'display_subscribers_count', 'display_recipes_count'
    )
    search_fields = ('email', 'username')

    def display_subscribers_count(self, obj):
        return obj.subscribing.count()

    def display_recipes_count(self, obj):
        return obj.recipes.count()

    display_subscribers_count.short_description = 'Кол-во подписчиков'
    display_recipes_count.short_description = 'Кол-во рецептов'


admin.site.register(Subscribe)
