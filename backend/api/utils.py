from collections import OrderedDict

from django.db.models import Model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ValidationError

from core.constants import (
    TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR,
    TEMPLATE_MESSAGE_UNIQUE_ERROR
)


def object_update(*, serializer: Serializer) -> Response:

    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        serializer.data, status=status.HTTP_201_CREATED
    )


def object_delete(
    *,
    data: dict[str: object],
    error_message: str,
    model: Model
) -> Response:

    instance = model.objects.filter(**data)
    if not instance.exists():
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def many_unique_with_minimum_one_validate(
    data_list: list, field_name: str, singular: str, plural: str
) -> None:

    if not data_list:
        raise ValidationError({
            field_name: TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR.format(
                field_name=singular.lower()
            )
        })

    if isinstance(data_list[0], OrderedDict):
        data_set = {data['id'] for data in data_list}
    else:
        data_set = {data.id for data in data_list}

    if len(data_list) != len(data_set):
        raise ValidationError({
            field_name: TEMPLATE_MESSAGE_UNIQUE_ERROR.format(
                field_name=plural.capitalize()
            )
        })
