from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.serializers import TagSerializer
from recipes.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
