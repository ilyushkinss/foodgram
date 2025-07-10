from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from users.admin.subscription import SubscriptionAdmin
from users.admin.user import UserAdmin

admin.site.unregister(Group)
admin.site.unregister(TokenProxy)

__all__ = ['SubscriptionAdmin', 'UserAdmin']
