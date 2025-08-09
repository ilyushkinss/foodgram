from django.db.models import Model
from rest_framework.permissions import (SAFE_METHODS,
                                        BasePermission,
                                        )
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet


class ReadOnly(BasePermission):

    def has_permission(self, request: Request, view: GenericViewSet) -> bool:
        return request.method in SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает:
    - Чтение всем
    - Запись только автору объекта
    """
    def has_object_permission(
        self, request: Request, view: GenericViewSet, obj: Model
    ) -> bool:
        return request.method in SAFE_METHODS or obj.author == request.user
