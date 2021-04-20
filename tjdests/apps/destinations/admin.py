from django.contrib import admin

from .models import College, Decision, TestScore


class CollegeAdmin(admin.ModelAdmin):
    search_fields = ["ceeb_code", "name", "location"]


admin.site.register(College, CollegeAdmin)
admin.site.register(TestScore)
admin.site.register(Decision)
