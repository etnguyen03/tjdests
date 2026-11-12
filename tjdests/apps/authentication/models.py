from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from ..destinations.models import Decision


class User(AbstractUser):
    accepted_terms = models.BooleanField(default=False)
    graduation_year = models.PositiveSmallIntegerField(default=0)

    GPA = models.DecimalField(
        null=True,
        blank=True,
        name="GPA",
        help_text="Pre-senior year, weighted GPA",
        max_digits=4,
        decimal_places=3,
    )

    is_student = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    nickname = models.CharField(max_length=30, blank=True)
    use_nickname = models.BooleanField(
        default=False,
        verbose_name="Use nickname instead of first name",
        help_text="If this is set, your nickname will be used to identify you across the site.",
    )

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

    preferred_name = models.CharField(max_length=30, blank=True)

    use_additional_hashes = models.BooleanField(
        default=False,
        verbose_name="Allow additional password hashes",
        help_text="If enabled, user can authenticate with additional password hashes stored in "
        "PasswordHash table.",
    )

    def get_preferred_name(self):
        return self.nickname if self.nickname and self.use_nickname else self.first_name

    @property
    def is_senior(self):
        """
        Determine if user is a senior based on graduation year.
        Returns True if graduation year matches current academic year:
        - Jan-Jul: current calendar year
        - Aug-Dec: current calendar year + 1
        """
        if not self.graduation_year or self.graduation_year == 0:
            return False

        now = timezone.now()
        current_year = now.year

        # Determine current academic year
        if now.month >= 8:  # Aug-Dec
            current_academic_year = current_year + 1
        else:  # Jan-Jul
            current_academic_year = current_year

        return self.graduation_year == current_academic_year

    @property
    def can_update_profile(self):
        """
        Determine if user can update their profile.
        Returns True if graduation year is less than or equal to current academic year.
        """
        if not self.graduation_year or self.graduation_year == 0:
            return False

        now = timezone.now()
        current_year = now.year

        # Determine current academic year
        if now.month >= 8:  # Aug-Dec
            current_academic_year = current_year + 1
        else:  # Jan-Jul
            current_academic_year = current_year

        return self.graduation_year <= current_academic_year

    def __str__(self):
        return f"{self.preferred_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.preferred_name = self.get_preferred_name()
        super().save(*args, **kwargs)


class PasswordHash(models.Model):
    """Additional password hashes for a user."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="additional_hashes"
    )
    password_hash = models.CharField(max_length=128, help_text="Hashed password string")
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Password Hash"
        verbose_name_plural = "Password Hashes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Hash for {self.user.username} (created: {self.created_at.strftime('%Y-%m-%d')})"
