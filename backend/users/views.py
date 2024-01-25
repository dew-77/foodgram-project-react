from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.paginators import CustomPageNumberPagination
from .models import Subscribe
from .serializers import UserRecipeSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        self.check_permissions(request)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribing__subscriber=self.request.user
        )
        page = self.paginate_queryset(queryset)
        serializer = UserRecipeSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        subscribing_user = get_object_or_404(User, pk=id)
        serializer = UserRecipeSerializer(
            subscribing_user, data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(
            subscriber=request.user,
            subscribing=subscribing_user
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        try:
            subscribing_user = get_object_or_404(User, pk=id)
            subscription = Subscribe.objects.get(
                subscriber=request.user, subscribing=subscribing_user)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            # 400 - по ТЗ вместо 404
            return Response(
                {'detail': 'The subscription does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
