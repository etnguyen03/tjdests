from django.contrib import admin

from .models import College, Decision, TestScore


class CollegeAdmin(admin.ModelAdmin):
    search_fields = ["name", "location"]
    list_display = ["name", "location"]


class DecisionAdmin(admin.ModelAdmin):
    list_display = [
        "college",
        "decision_type",
        "admission_status",
        "user",
        "last_modified",
    ]
    list_filter = ["decision_type", "admission_status"]

    readonly_fields = ["last_modified"]


class TestScoreAdmin(admin.ModelAdmin):
    list_display = ["exam_type", "exam_score", "user", "last_modified"]
    list_filter = ["exam_type"]

    readonly_fields = ["last_modified"]


admin.site.register(College, CollegeAdmin)
admin.site.register(TestScore, TestScoreAdmin)
admin.site.register(Decision, DecisionAdmin)
