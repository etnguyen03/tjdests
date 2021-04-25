from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ["username", "first_name", "last_name"]
    list_display = ["username", "last_name", "first_name", "last_modified"]
    list_filter = ["is_senior", "is_student", "accepted_terms", "publish_data"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                    "accepted_terms",
                    "is_staff",
                    "is_superuser",
                    "is_senior",
                    "graduation_year",
                    "is_student",
                    "last_modified",
                    "last_login",
                )
            },
        ),
        (
            "Senior information",
            {"fields": ("biography", "attending_decision", "publish_data")},
        ),
    )

    readonly_fields = (
        "last_modified",
        "last_login",
    )


admin.site.register(User, UserAdmin)
