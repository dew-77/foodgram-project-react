from django_filters import rest_framework as filters
from .models import Tag


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='in_favorites')
    is_in_shopping_cart = filters.BooleanFilter(
        method='in_shopping_cart'
    )

    def in_favorites(self, queryset, name, obj):
        if (not self.request.user.is_authenticated) or (not obj):
            return queryset
        return queryset.filter(favorites__user=self.request.user)

    def in_shopping_cart(self, queryset, name, obj):
        if (not self.request.user.is_authenticated) or (not obj):
            return queryset
        return queryset.filter(carts__user=self.request.user)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
