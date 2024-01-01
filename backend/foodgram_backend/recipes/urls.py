from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
)

router = DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
