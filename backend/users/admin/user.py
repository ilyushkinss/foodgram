from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (UserCreationForm,
                                       UserChangeForm)
from django.contrib.auth import update_session_auth_hash

from recipes.models import RecipeFavorite, ShoppingCart
from users.models.user import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя с видимыми полями пароля"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.TextInput(
            attrs={'class': 'vTextField'}
        )
        self.fields['password2'].widget = forms.TextInput(
            attrs={'class': 'vTextField'}
        )
        self.fields['password1'].help_text = "Введите пароль"
        self.fields['password2'].help_text = "Подтвердите пароль"


class CustomUserChangeForm(UserChangeForm):
    """Форма для редактирования пользователя"""
    password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'vTextField'}),
        required=False,
        help_text="Введите новый пароль (оставьте пустым, чтобы не менять)"
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user_permissions' in self.fields:
            del self.fields['user_permissions']
        if 'groups' in self.fields:
            del self.fields['groups']


class RecipeFavoriteInline(admin.TabularInline):
    """Инлайн для избранных рецептов пользователя"""
    model = RecipeFavorite
    autocomplete_fields = ['recipe']
    extra = 1
    verbose_name = "Избранный рецепт"
    verbose_name_plural = "Избранные рецепты"


class ShoppingCartInline(admin.TabularInline):
    """Инлайн для корзины покупок пользователя"""
    model = ShoppingCart
    autocomplete_fields = ['recipe']
    extra = 1
    verbose_name = "Товар в корзине"
    verbose_name_plural = "Корзина покупок"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'username', 'email', 'get_full_name', 'last_login',
        'is_active', 'is_staff'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('id',)
    readonly_fields = ('date_joined', 'last_login')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return [
                (None, {
                    'fields': ('username', 'password1', 'password2')
                }),
                ('Персональная информация', {
                    'fields': ('first_name', 'last_name', 'email')
                }),
                ('Права доступа', {
                    'fields': ('is_active', 'is_staff', 'is_superuser'),
                    'classes': ('collapse',)
                }),
            ]
        else:
            return [
                (None, {
                    'fields': ('username', 'password')
                }),
                ('Персональная информация', {
                    'fields': ('first_name', 'last_name', 'email')
                }),
                ('Права доступа', {
                    'fields': ('is_active', 'is_staff', 'is_superuser'),
                    'classes': ('collapse',)
                }),
                ('Важные даты', {
                    'fields': ('last_login', 'date_joined'),
                    'classes': ('collapse',)
                }),
            ]

    def save_model(self, request, obj, form, change):
        """Обработка сохранения пароля"""
        if (change and 'password' in form.cleaned_data
                and form.cleaned_data['password']):
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def change_view(self, request, object_id, extra_context=None):
        """Добавляем inline-формы при редактировании"""
        self.inlines = [RecipeFavoriteInline, ShoppingCartInline]
        return super().change_view(request, object_id, extra_context)

    def response_change(self, request, obj):
        """Обновляем сессию, если меняем свой пароль"""
        if 'password' in request.POST and request.POST['password']:
            if obj == request.user:
                update_session_auth_hash(request, obj)
        return super().response_change(request, obj)

    def get_inline_instances(self, request, obj=None):
        """Возвращаем inline-формы только при редактировании"""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)