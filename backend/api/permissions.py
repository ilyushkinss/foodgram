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
    def has_permission(self, request: Request, view: GenericViewSet) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(
        self, request: Request, view: GenericViewSet, obj: Model
    ) -> bool:
        return request.method in SAFE_METHODS or obj.author == request.user
