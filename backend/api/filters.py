from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """Фильтр по названию ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


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
        if not hasattr(self, "request") or not hasattr(self.request, "user"):
            return queryset.none()

        author = self.request.user
        if not author.is_authenticated:
            return queryset.all()

        if value:
            return queryset.filter(**{filter_field: author}).distinct()
        return queryset.exclude(**{filter_field: author})

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
