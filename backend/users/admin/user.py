from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import update_session_auth_hash

from recipes.models import RecipeFavorite, ShoppingCart
from users.models.user import User


class UserAdminForm(forms.ModelForm):
    """Форма пользователя с полем для смены пароля"""
    new_password = forms.CharField(
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
        if not self.instance.pk:
            self.fields['password'].widget = forms.TextInput(
                attrs={'class': 'vTextField'}
            )
            self.fields['password'].help_text = "Введите новый пароль"
            del self.fields['new_password']
        elif 'password' in self.fields:
            del self.fields['password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if ('new_password' in self.cleaned_data
                and self.cleaned_data['new_password']):
            user.set_password(self.cleaned_data['new_password'])
        elif not user.pk:  # Для нового пользователя
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class RecipeFavoriteInline(admin.TabularInline):
    model = RecipeFavorite
    autocomplete_fields = ['recipe']
    extra = 1


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    autocomplete_fields = ['recipe']
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    list_display = (
        'username', 'email', 'get_full_name', 'last_login',
        'is_active', 'is_staff'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('id',)
    readonly_fields = ('date_joined', 'last_login')
    exclude = ('groups', 'user_permissions')

    def get_fieldsets(self, request, obj=None):
        """Динамические fieldsets с добавлением поля нового пароля"""
        if obj:  # Редактирование
            fieldsets = [
                ('Персональные данные', {
                    'fields': ('username', 'email', 'first_name',
                               'last_name', 'new_password')
                }),
                ('Признаки', {
                    'fields': ('is_active', 'is_staff', 'is_superuser')
                }),
                ('Служебная информация', {
                    'fields': ('date_joined', 'last_login')
                })
            ]
        else:  # Создание
            fieldsets = [
                ('Персональные данные', {
                    'fields': ('username', 'email', 'first_name',
                               'last_name', 'password')
                }),
                ('Признаки', {
                    'fields': ('is_active', 'is_staff', 'is_superuser')
                })
            ]
        return fieldsets

    def add_view(self, request, extra_content=None):
        """При создании пользователя"""
        return super().add_view(request, extra_content)

    def change_view(self, request, object_id, extra_content=None):
        """При редактировании добавляем inline-формы"""
        self.inlines = [RecipeFavoriteInline, ShoppingCartInline]
        return super().change_view(request, object_id, extra_content)

    def response_change(self, request, obj):
        """Обновляем сессию, если меняем свой пароль"""
        if 'new_password' in request.POST and request.POST['new_password']:
            if obj == request.user:
                update_session_auth_hash(request, obj)
        return super().response_change(request, obj)
