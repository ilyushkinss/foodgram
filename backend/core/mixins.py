from django.db import models

from rest_framework import status
from rest_framework.response import Response


class ObjectCRUDMixin:
    """Миксин для общих операций CRUD"""

    @staticmethod
    def object_update(*, serializer) -> Response:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def object_delete(
            *,
            data: dict[str, models.Model],
            error_message: str,
            model: models.Model
    ) -> Response:
        instance = model.objects.filter(**data)
        if not instance.exists():
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
