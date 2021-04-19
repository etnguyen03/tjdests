from django.contrib import admin

from .models import College, Decision, TestScore

admin.site.register(College)
admin.site.register(TestScore)
admin.site.register(Decision)
