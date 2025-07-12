from django.contrib import admin

from recipes.models.tag import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Управление тегами в админ-зоне."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name',)
