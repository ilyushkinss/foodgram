from re import sub as re_sub
from uuid import uuid4

from core.constants import MAX_LENGTH_SHORT_LINK


def generate_short_link() -> str:

    return uuid4().hex[:MAX_LENGTH_SHORT_LINK]


def to_snake_case(text: str) -> str:

    return re_sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
