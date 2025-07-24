from djoser import views as djoser_views
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from django.shortcuts import get_object_or_404

from api.permissions import ReadOnly
from api.serializers import (AvatarSerializer, UserSerializer,
                             SubscriptionGetSerializer, SubscriptionChangedSerializer)
from users.models import User, Subscription
from ..utils import object_delete, object_update


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'
    permission_classes = [IsAuthenticated | ReadOnly]

    @action(
        ['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    def get_data(self, request: Request, id: int) -> dict:
        return {
            'user': request.user,
            'author_recipe': get_object_or_404(User, id=id)
        }

    @action(['GET'], detail=False, url_path='subscriptions')
    def subscriptions(self, request: Request):
        user = request.user
        queryset = User.objects.filter(authors__user=user)
        pages = self.paginate_queryset(queryset)

        serializer = SubscriptionGetSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def post_subscribe(self, request: Request, id: int):
        data: dict = self.get_data(request=request, id=id)
        serializer = SubscriptionChangedSerializer(
            data={key: obj.id for key, obj in data.items()},
            context={'request': request}
        )
        return object_update(serializer=serializer)

    @post_subscribe.mapping.delete
    def delete_subscribe(self, request: Request, id: int):
        return object_delete(
            data=self.get_data(request=request, id=id),
            error_mesage='У вас нет данного пользователя в подписчиках.',
            model=Subscription
        )

    @action(
        ['PUT'],
        detail=False,
        url_path='me/avatar',
        name='set_avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request: Request, *args, **kwargs):
        if 'avatar' not in request.data:
            return response.Response(
                {'avatar': 'Отсутствует изображение'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_data = serializer.validated_data.get('avatar')
        request.user.avatar = avatar_data
        request.user.save()

        image_url = request.build_absolute_uri(
            f'/media/users/{avatar_data.name}'
        )
        return response.Response(
            {'avatar': str(image_url)}, status=status.HTTP_201_CREATED
        )

    @avatar.mapping.delete
    def delete_avatar(self, request: Request, *args, **kwargs):
        user = self.request.user
        if user.avatar:
            user.avatar.delete()
            # На мой взгляд, две следующие строки необходимы, ведь иначе
            # поле avatar в бд осанется со ссылкой на несуществующий файл
            # и при следующем обращении выдаст ошибку.
            user.avatar = None
            user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
