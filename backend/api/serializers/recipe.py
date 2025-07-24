from typing import Optional

from django.db.models import Model
from rest_framework import serializers
from rest_framework.request import Request

from api.serializers.base_serializers import BaseRecipeSerializer
from api.serializers.recipe_ingredients import (
    RecipeIngredientsGetSerializer
)
from api.serializers.tag import TagSerializer
from api.serializers.user import UserSerializer
from core.constants import MAX_INTEGER_VALUE, MIN_INTEGER_VALUE
from recipes.models import (
    Recipe,
    RecipeFavorite,
    RecipeIngredients,
    ShoppingCart,
    Tag
)


class RecipeSerializer(BaseRecipeSerializer):
    """Сериализатор рецептов."""
    class Meta(BaseRecipeSerializer.Meta):
        abstract = True
        fields = (
            *BaseRecipeSerializer.Meta.fields,
            'tags', 'ingredients', 'author', 'text'
        )
        read_only_fields = fields


class RecipeGetSerializer(RecipeSerializer):
    """Сериализатор рецептов GET-запросов и для ответов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsGetSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeSerializer.Meta):
        fields = (
            *RecipeSerializer.Meta.fields,
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = fields

    def get_is_exists(self, obj: Recipe, model: Model):
        request: Optional[Request] = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(
            author=request.user, recipe=obj
        ).exists()

    def get_is_favorited(self, obj: Recipe):
        return self.get_is_exists(obj, RecipeFavorite)

    def get_is_in_shopping_cart(self, obj: Recipe):
        return self.get_is_exists(obj, ShoppingCart)


class RecipeChangeSerializer(RecipeSerializer):
    """Сериализатор изменения рецептов"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
    )
    author = UserSerializer(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        source='recipe_ingredients',
        required=True,
        write_only=True
    )
    cooking_time = serializers.IntegerField(
        max_value=MAX_INTEGER_VALUE,
        min_value=MIN_INTEGER_VALUE,
        error_messages={
            'min_value':
                f'Минимальное время приготовления - {MIN_INTEGER_VALUE} мин.',
            'max_value':
                f'Максимальное время приготовления - {MAX_INTEGER_VALUE} мин.',
        }
    )
    name = serializers.CharField(required=True)

    text = serializers.CharField(required=True)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + (
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'author',
            'tags'
        )

    def validate(self, data):
        ingredients = data.get('recipe_ingredients', [])
        tags = data.get('tags', [])

        # Валидация ингредиентов
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Необходимо указать хотя бы один ингредиент.'}
            )

        seen_ingredients = set()
        for ing in ingredients:
            ingredient_id = self._get_ingredient_id(ing)
            if ingredient_id in seen_ingredients:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты должны быть уникальными.'}
                )
            seen_ingredients.add(ingredient_id)

        # Валидация тегов
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Необходимо указать хотя бы один тег.'}
            )

        return data

    def _get_ingredient_id(self, ingredient_data):
        """Универсальное получение ID ингредиента из разных форматов данных"""
        if isinstance(ingredient_data.get('ingredient'), dict):
            return ingredient_data['ingredient']['id']
        elif isinstance(ingredient_data.get('ingredient'), (int, str)):
            return int(ingredient_data['ingredient'])
        elif 'id' in ingredient_data:
            return ingredient_data['id']
        else:
            raise serializers.ValidationError(
                {'ingredients': 'Неверный формат данных ингредиента.'}
            )

    def _get_ingredient_amount(self, ingredient_data):
        """Получение количества ингредиента"""
        try:
            return int(ingredient_data['amount'])
        except (KeyError, ValueError):
            raise serializers.ValidationError(
                {'amount': 'Необходимо указать количество ингредиента.'}
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient_id=self._get_ingredient_id(ingredient_data),
                amount=self._get_ingredient_amount(ingredient_data)
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredients.objects.create(
                    recipe=instance,
                    ingredient_id=self._get_ingredient_id(ingredient_data),
                    amount=self._get_ingredient_amount(ingredient_data)
                )

        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data
