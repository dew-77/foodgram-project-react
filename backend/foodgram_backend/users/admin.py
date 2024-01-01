from django.contrib import admin
from .models import CustomUser, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'is_superuser', 'first_name', 'last_name'
    )
    search_fields = ('email', 'username')


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscribe)
