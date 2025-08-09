from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag

User = get_user_model()


class IngredientFilter(SearchFilter):
    """Фильтр для полнотекстового поиска ингредиентов."""
    search_param = 'name'
    search_title = 'Название'

    def get_search_fields(self, view, request):
        return ['^name']


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов."""
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_or_exclude_author(
            self, queryset: QuerySet, name: str, value: bool, filter_field: str
    ) -> QuerySet:
        if not value:
            return queryset

        if (not getattr(self.request, 'user', None)
                or not self.request.user.is_authenticated):
            return queryset.none()

        return queryset.filter(**{filter_field: self.request.user}).distinct()

    def filter_is_favorited(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return self.filter_or_exclude_author(
            queryset, name, value, filter_field='recipe_favorite__author'
        )

    def filter_is_in_shopping_cart(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return self.filter_or_exclude_author(
            queryset, name, value, filter_field='shopping_cart__author'
        )
