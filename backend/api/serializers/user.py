from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers


class CurrentUserSerializer(DjoserUserSerializer):
    """Сериализатор текущего пользователя."""

    is_subscribed = serializers.BooleanField(default=False, read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        # model = User
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',)


class UserSerializer(CurrentUserSerializer):
    """Общий Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (request and request.user.is_authenticated and
                obj.authors.filter(user=request.user).exists())
