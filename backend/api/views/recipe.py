import csv
from datetime import datetime

from django.shortcuts import get_object_or_404, redirect
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly, ReadOnly
from api.serializers import (RecipeChangeSerializer,
                             RecipeGetSerializer,
                             DownloadShoppingCartSerializer,
                             ShoppingCartSerializer,
                             RecipeFavoriteSerializer)
from recipes.models import Recipe, ShoppingCart, RecipeFavorite
from core.mixins import ObjectCRUDMixin


class RecipeViewSet(viewsets.ModelViewSet,
                    ObjectCRUDMixin):
    """Вьюсет для рецептов и связных с /recipes/ действий."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    serializer_class = RecipeChangeSerializer
    ordering = ['-id']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    search_fields = ['title', 'tag']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    RecipeFavorite.objects.filter(
                        author=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        author=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )

        return queryset

    def get_permissions(self):
        if self.action == 'download_shopping_cart':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer: Serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request: Request, pk: int):
        try:
            recipe: Recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response(
                {'message': 'Не существует такой записи'},
                status=status.HTTP_404_NOT_FOUND
            )

        scheme = request.scheme
        host = request.get_host()
        domain = f'{scheme}://{host}'
        return Response(
            {'short-link': f'{domain}/s/{recipe.short_link}'},
            status=status.HTTP_200_OK
        )

    def get_data(self, request: Request, pk: int) -> dict:
        return {
            'author': request.user,
            'recipe': get_object_or_404(Recipe, id=pk)
        }

    @action(detail=True, methods=['POST'], url_path='favorite')
    def post_favorite(self, request: Request, pk: int):
        data: dict = self.get_data(request=request, pk=pk)
        serializer = RecipeFavoriteSerializer(
            data={key: obj.id for key, obj in data.items()},
            context={'request': request}
        )
        return self.object_update(serializer=serializer)

    @post_favorite.mapping.delete
    def delete_favorite(self, request: Request, pk: int):
        return self.object_delete(
            data=self.get_data(request=request, pk=pk),
            error_message='У вас нет данного рецепта в избранном.',
            model=RecipeFavorite
        )

    def get_favorite_data(self, request: Request, pk: int) -> dict:
        """Общая часть для получения данных favorite."""
        return {
            'author': request.user,
            'recipe': get_object_or_404(Recipe, id=pk)
        }

    @action(detail=True, methods=['POST'], url_path='favorite')
    def post_favorite(self, request: Request, pk: int):
        data = self.get_favorite_data(request, pk)
        serializer = RecipeFavoriteSerializer(
            data={key: obj.id for key, obj in data.items()},
            context={'request': request}
        )
        return self.object_update(serializer=serializer)

    def get_serializer_class(self):
        if self.action == "post_shopping_cart":
            return ShoppingCartSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['POST'], url_path='shopping_cart')
    def post_shopping_cart(self, request: Request, pk: int) -> Response:
        data: dict = self.get_data(request=request, pk=pk)
        serializer = self.get_serializer(
            data={key: obj.id for key, obj in data.items()},
            context={'request': request}
        )
        return self.object_update(serializer=serializer)

    @post_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request: Request, pk: int):
        return self.object_delete(
            data=self.get_data(request=request, pk=pk),
            error_message='У вас нет данного рецепта в корзине.',
            model=ShoppingCart
        )

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        serializer = DownloadShoppingCartSerializer(
            instance=ShoppingCart.objects.all(),
            many=True, context={'request': request}
        )

        now = datetime.now()
        formatted_time = now.strftime('%d-%m-%Y_%H_%M_%S')

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f'shopping_cart_{request.user.id}_{formatted_time}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])

        if serializer.data:
            ingredients = serializer.data[0]['ingredients']
            rows = [
                [
                    ingredient['name'],
                    ingredient['measurement_unit'],
                    ingredient['total_amount']
                ] for ingredient in ingredients
            ]
            writer.writerows(rows)

        return response


class RecipeRedirectView(APIView):
    """
    Вьюсет редиректа с короткой ссылки рецепта на абсолютный адрес.
    """

    permission_classes = [ReadOnly]

    def get(self, request: Request, short_link: str):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect(recipe.get_frontend_absolute_url())
