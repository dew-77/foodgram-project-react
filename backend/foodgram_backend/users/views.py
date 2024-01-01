from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subscribe
from .paginators import UsersPageNumberPagination
from .serializers import UserRecipeSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = UsersPageNumberPagination

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

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        subscribing_user = get_object_or_404(User, pk=id)

        if request.method == 'POST':
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

        elif request.method == 'DELETE':
            try:
                subscription = Subscribe.objects.get(
                    subscriber=request.user, subscribing=subscribing_user)
            except Subscribe.DoesNotExist:
                return Response(
                    {"errors": "Subscription not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription.delete()

            return Response(
                {"message": "Subscription deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
