from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError


class SubscribeUniqueValidator:
    def __init__(self, fields: list,
                 message: str = 'Невозможно подписаться на самого себя'):
        self.fields = fields
        self.message = message

    def __call__(self, attrs: dict):
        user = attrs.get('user')
        author_recipe = attrs.get('author_recipe')

        if user == author_recipe:
            raise ValidationError(self.message)


def validate_min_one_unique(items: list, field_name: str, name_forms: tuple):
    """Общий валидатор для проверки минимум одного уникального элемента."""
    if not items:
        raise ValidationError({
            field_name: f"Должен быть указан хотя бы один {name_forms[0]}."
        })

    if len(items) != len(set(item.id for item in items)):
        raise ValidationError({
            field_name: f"{name_forms[1]} должны быть уникальными."
        })
