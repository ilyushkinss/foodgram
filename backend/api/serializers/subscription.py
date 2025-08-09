from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.serializers.base_serializers import BaseRecipeSerializer
from api.serializers.user import UserSerializer
from api.validators import SubscribeUniqueValidator
from users.models import Subscription, User


class SubscriptionGetSerializer(UserSerializer):
    """Сериализатор подписчиков. Только для чтения."""

    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.IntegerField(
        source='recipes.count'
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = fields

    def get_recipes(self, obj: User):
        if 'request' not in self.context:
            raise serializers.ValidationError(
                {"error": "Отсутствует request в контексте сериализатора."},
                code="missing_request_context"
            )

        request = self.context['request']
        recipes_limit = None

        try:
            recipes_limit = int(request.GET.get('recipes_limit', ''))
        except (ValueError, TypeError):
            recipes_limit = settings.RECIPES_LIMIT_MAX

        queryset = obj.recipes.all()
        if recipes_limit is not None:
            queryset = queryset[:recipes_limit]

        serializer = BaseRecipeSerializer
        return serializer(queryset, many=True).data


class SubscriptionChangedSerializer(serializers.ModelSerializer):
    """Сериализатор подписчиков. Только на запись."""

    class Meta:
        model = Subscription
        fields = ('author_recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author_recipe', 'user'),
                message='Нельзя повторно подписаться на пользователя'
            ),
            SubscribeUniqueValidator(
                fields=('author_recipe', 'user')
            )
        ]

    def to_representation(self, instance):
        return SubscriptionGetSerializer(
            instance.author_recipe,
            context=self.context
        ).data
