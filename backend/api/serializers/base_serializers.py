import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.serializers.user import UserSerializer
from recipes.models.abstract_models import BaseActionRecipeModel
from recipes.models.recipe import Recipe
from drf_extra_fields.fields import Base64ImageField


class AvatarSerializer(serializers.Serializer):
    """Сериализатор для аватарки."""

    avatar = Base64ImageField(required=False)


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов и авторов в связанные таблицы."""

    author = UserSerializer
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = None
        fields = ('author', 'recipe')
        error_message = ''

    @classmethod
    def get_validators(cls):
        return [
            UniqueTogetherValidator(
                queryset=cls.Meta.model.objects.all(),
                fields=('author', 'recipe'),
                message=cls.Meta.error_message
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.validators = self.get_validators()

    def to_representation(self, instance: BaseActionRecipeModel):
        return BaseRecipeSerializer(instance.recipe).data
