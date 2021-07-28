from django.contrib.auth.models import AbstractUser
from django.db import models

from ..destinations.models import Decision


class User(AbstractUser):
    accepted_terms = models.BooleanField(default=False)
    graduation_year = models.PositiveSmallIntegerField(null=True)

    gpa = models.FloatField(null=True, blank=True, name="GPA", help_text="Weighted GPA")

    is_senior = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    nickname = models.CharField(max_length=30, blank=True)

    # The rest are used only if a senior
    publish_data = models.BooleanField(
        default=False,
        verbose_name="Publish my data",
        help_text="Unless this is set, your data will not appear publicly.",
    )
    biography = models.TextField(blank=True, max_length=1500)

    attending_decision = models.ForeignKey(
        Decision,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="College attending",
        related_name="attending_college",
        help_text="Can't see your college? Make sure you've added a decision with an admit status.",
    )

    last_modified = models.DateTimeField(auto_now=True)

    @property
    def preferred_name(self):
        return self.nickname if self.nickname else self.first_name

    def __str__(self):
        return f"{self.preferred_name} {self.last_name}"
