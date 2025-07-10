from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import (
    MAX_INGREDIENT_AMOUNT_ERROR,
    MAX_INTEGER_VALUE,
    MIN_INGREDIENT_AMOUNT_ERROR,
    MIN_INTEGER_VALUE
)
from recipes.models.base_models import CookbookBaseModel
from recipes.models.ingredient import Ingredient
from recipes.models.recipe import Recipe
from users.models.user import User


class RecipeIngredientsQuerySet(models.QuerySet):
    """QuerySet модели-связи рецептов и ингредиентов."""

    def get_sum_amount(self) -> 'RecipeIngredientsQuerySet':
        return self.annotate(total_amount=models.Sum('amount'))

    def order_by_ingredient_name(self) -> 'RecipeIngredientsQuerySet':
        return self.order_by('ingredient__name')

    def rename_fields(self) -> 'RecipeIngredientsQuerySet':
        return self.values(
            name=models.F('ingredient__name'),
            measurement_unit=models.F('ingredient__measurement_unit')
        )


class ShopCartListManager(models.Manager):
    """
    Manager модели-связи рецептов и ингредиентов.

    Используется для получения список ингредиентов для покупок.
    """

    def get_queryset(self, author: User) -> RecipeIngredientsQuerySet:
        return (
            RecipeIngredientsQuerySet(self.model)
            .filter(recipe__shopping_cart__author=author)
            .rename_fields()
            .get_sum_amount()
            .order_by_ingredient_name()
        )


class RecipeIngredients(CookbookBaseModel):
    """Модель связи рецептов и ингредиентов."""

    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        to=Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в рецепте',
        validators=[
            MinValueValidator(
                MIN_INTEGER_VALUE,
                message=MIN_INGREDIENT_AMOUNT_ERROR
            ),
            MaxValueValidator(
                MAX_INTEGER_VALUE,
                message=MAX_INGREDIENT_AMOUNT_ERROR
            )
        ]
    )

    objects = RecipeIngredientsQuerySet.as_manager()
    shopping_list = ShopCartListManager()

    class Meta(CookbookBaseModel.Meta):
        default_related_name = 'recipe_ingredients'
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Связь ингредиентов с рецептами'

    def __str__(self):
        return f'Рецепт #{self.recipe.id} - Ингредиент #{self.ingredient.id}'
