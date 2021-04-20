from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ["username", "first_name", "last_name"]


admin.site.register(User, UserAdmin)
