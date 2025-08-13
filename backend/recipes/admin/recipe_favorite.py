from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from recipes.models.recipe_favorite import RecipeFavorite


@admin.register(RecipeFavorite)
class RecipeFavoriteAdmin(admin.ModelAdmin):
    """Админ-панель для избранных рецептов."""

    list_display = ('id', 'get_author', 'get_recipe')
    list_filter = ('author',)
    search_fields = (
        'recipe__name', 'author__username',
        'author__first_name', 'author__last_name'
    )
    empty_value_display = '-пусто-'

    def get_author(self, obj):
        url = reverse('admin:users_user_change', args=[obj.author.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author.__str__()
        )
    get_author.short_description = 'Пользователь'

    def get_recipe(self, obj):
        url = reverse('admin:recipes_recipe_change', args=[obj.recipe.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.recipe.__str__()
        )
    get_recipe.short_description = 'Рецепт'
