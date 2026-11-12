from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from .models import User


class AdditionalHashBackend(ModelBackend):
    """
    Authentication backend that checks additional password hashes
    when use_additional_hashes is enabled for a user.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        # First try the standard password authentication
        if user.check_password(password):
            return user if self.user_can_authenticate(user) else None

        # If standard auth fails and additional hashes are enabled, check those
        if user.use_additional_hashes:
            additional_hashes = user.additional_hashes.all()

            for password_hash_obj in additional_hashes:
                if check_password(password, password_hash_obj.password_hash):
                    # Update last_used timestamp
                    password_hash_obj.last_used = timezone.now()
                    password_hash_obj.save(update_fields=["last_used"])

                    # Set session flag to indicate password reset is needed
                    if request:
                        request.session["needs_password_reset"] = True

                    return user if self.user_can_authenticate(user) else None

        return None
