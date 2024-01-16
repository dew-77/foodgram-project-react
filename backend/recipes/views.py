from django.http import HttpResponse
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.decorators import action
from rest_framework.response import Response
from .filters import IngredientFilter, RecipeFilter
from .models import Recipe, Tag, Ingredient, Cart, RecipeIngredient, Favorite
from .paginators import SubscriptionsPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    TagSerializer, RecipeCreateSerializer, RecipeReadSerializer,
    IngredientSerializer, RecipeToCartSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = SubscriptionsPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Cart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Recipe already added into cart."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Cart.objects.create(user=user, recipe=recipe)

            serializer = RecipeToCartSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                cart_item = Cart.objects.get(user=user, recipe=recipe)
            except Cart.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found in the cart."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.delete()

            return Response(
                {"message": "Recipe removed from the cart."},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            url_name='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user

        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Recipe already added into Favorite."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favorite.objects.create(user=user, recipe=recipe)

            serializer = RecipeToCartSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            try:
                favorite_item = Favorite.objects.get(user=user, recipe=recipe)
            except Favorite.DoesNotExist:
                return Response(
                    {"errors": "Recipe not found in favorites."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite_item.delete()
            return Response(
                {"message": "Recipe removed from favorites."},
                status=status.HTTP_204_NO_CONTENT
            )

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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer


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
