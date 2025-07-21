from rest_framework import serializers

from core.constants import MAX_INTEGER_VALUE, MIN_INTEGER_VALUE
from recipes.models import Ingredient, RecipeIngredients


class RecipeIngredientsSetSerializer(serializers.ModelSerializer):
    """Сериализатор связующий рецепты и ингредиенты на запись."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        error_messages={
            'does_not_exist': 'Ингредиент с id={pk_value} не существует.',
            'incorrect_type': 'Некорректный тип данных для id ингредиента.'
        }
    )
    amount = serializers.IntegerField(
        max_value=MAX_INTEGER_VALUE,
        min_value=MIN_INTEGER_VALUE,
        error_messages={
            'min_value': f'Количество ингредиента не может быть меньше {MIN_INTEGER_VALUE}.',
            'max_value': f'Количество ингредиента не может превышать {MAX_INTEGER_VALUE}.',
        }
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientsGetSerializer(serializers.ModelSerializer):
    """Сериализатор связующий рецепты и ингредиенты на чтение."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
