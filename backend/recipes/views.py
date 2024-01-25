from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from .paginators import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, RecipeToCartSerializer,
                          TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def create_object(request, pk, type):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"errors": "Recipe not found."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if type == 'cart':
            cart_serializer = CartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            cart_serializer.is_valid(raise_exception=True)
            cart_serializer.save()
        elif type == 'favorite':
            favorite_serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            favorite_serializer.is_valid(raise_exception=True)
            favorite_serializer.save()
        serializer = RecipeToCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(request, pk, type):
        recipe = get_object_or_404(Recipe, pk=pk)
        if type == 'cart':
            try:
                object_to_remove = Cart.objects.get(
                    user=request.user, recipe=recipe)
            except Cart.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found in the cart."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif type == 'favorite':
            try:
                object_to_remove = Favorite.objects.get(
                    user=request.user, recipe=recipe)
            except Favorite.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found in the favorites."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        object_to_remove.delete()

        return Response(
            {"message": "Recipe removed."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=['post'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.create_object(
            request, pk, 'cart')

    @action(methods=['post'], detail=True, url_path='favorite',
            url_name='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.create_object(
            request, pk, 'favorite')

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        return self.delete_object(
            request, pk, 'cart')

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_object(
            request, pk, 'favorite')

    @action(methods=['get'], detail=False,
            url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        aggregated_ingredients = {}
        for cart_item in cart_items:
            recipe = cart_item.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)

            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                if ingredient.name in aggregated_ingredients:
                    aggregated_ingredients[ingredient.name][
                        'quantity'] += recipe_ingredient.amount
                else:
                    aggregated_ingredients[ingredient.name] = {
                        'quantity': recipe_ingredient.amount,
                        'unit': ingredient.measurement_unit,
                    }

        cart_content = render_to_string(
            'shopping_cart.txt', {'ingredients': aggregated_ingredients})

        response = HttpResponse(cart_content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'

        return response


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
