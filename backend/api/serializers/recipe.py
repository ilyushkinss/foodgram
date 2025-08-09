from rest_framework import serializers

from api.serializers.base_serializers import BaseRecipeSerializer
from api.serializers.recipe_ingredients import (
    RecipeIngredientsGetSerializer,
    RecipeIngredientsSetSerializer,
)
from api.serializers.tag import TagSerializer
from api.serializers.user import UserSerializer
from core.constants import MAX_INTEGER_VALUE, MIN_INTEGER_VALUE
from recipes.models import (
    RecipeIngredients,
    Tag,
)


class RecipeSerializer(BaseRecipeSerializer):
    """Сериализатор рецептов."""
    class Meta(BaseRecipeSerializer.Meta):
        abstract = True
        fields = (
            *BaseRecipeSerializer.Meta.fields,
            'tags', 'ingredients', 'author', 'text'
        )
        read_only_fields = ('author',)


class RecipeGetSerializer(RecipeSerializer):
    """Сериализатор рецептов GET-запросов и для ответов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsGetSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True,
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta(RecipeSerializer.Meta):
        fields = (
            *RecipeSerializer.Meta.fields,
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = fields


class RecipeChangeSerializer(RecipeSerializer):
    """Сериализатор изменения рецептов"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
        error_messages={
            'does_not_exist':
                'Тега с id={pk_value} не существует.'
        }
    )
    author = UserSerializer(
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )
    ingredients = RecipeIngredientsSetSerializer(
        many=True,
        source='recipe_ingredients',
        required=True,
        write_only=True,
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

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + (
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'author',
            'tags'
        )

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один тег.'
            )
        unique_tags = set(tags)
        if len(unique_tags) != len(tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться'
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент.'
            )

        ingredient_ids = [ingredient['id'].id for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )
        return ingredients

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        """Создает все ингредиенты рецепта одним запросом"""
        recipe_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        recipe = super().create(validated_data)

        recipe.tags.set(tags_data)

        self._create_recipe_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)

        instance.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data
