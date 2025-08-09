from djoser import views as djoser_views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.permissions import ReadOnly
from api.serializers import (AvatarSerializer, UserSerializer,
                             SubscriptionGetSerializer,
                             SubscriptionChangedSerializer)
from users.models import User, Subscription
from core.mixins import ObjectCRUDMixin


class UserViewSet(djoser_views.UserViewSet, ObjectCRUDMixin):
    """Вьюсет пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'
    permission_classes = [IsAuthenticated | ReadOnly]

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return SubscriptionGetSerializer
        elif self.action in ['post_subscribe', 'delete_subscribe']:
            return SubscriptionChangedSerializer
        elif self.action == 'avatar':
            return AvatarSerializer
        return super().get_serializer_class()

    @action(['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    def get_data(self, request: Request, id: int) -> dict:
        return {
            'user': request.user,
            'author_recipe': get_object_or_404(User, id=id)
        }

    @action(['GET'], detail=False, url_path='subscriptions')
    def subscriptions(self, request: Request):
        queryset = User.objects.filter(authors__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def post_subscribe(self, request: Request, id: int):
        data = {key: obj.id for key, obj in self.get_data(request, id).items()}
        serializer = self.get_serializer(data=data)
        return self.object_update(serializer=serializer)

    @post_subscribe.mapping.delete
    def delete_subscribe(self, request: Request, id: int):
        return self.object_delete(
            data=self.get_data(request, id),
            error_message='У вас нет данного пользователя в подписчиках.',
            model=Subscription
        )

    @action(
        ['PUT'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request: Request, *args, **kwargs):
        if 'avatar' not in request.data:
            return Response(
                {'avatar': 'Отсутствует изображение'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.avatar = serializer.validated_data['avatar']
        request.user.save()

        image_url = request.build_absolute_uri(
            f'/media/users/{request.user.avatar.name}'
        )
        return Response(
            {'avatar': image_url},
            status=status.HTTP_201_CREATED
        )

    @avatar.mapping.delete
    def delete_avatar(self, request: Request, *args, **kwargs):
        if request.user.avatar:
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
