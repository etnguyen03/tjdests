from django.shortcuts import redirect
from django.urls import reverse


class PasswordResetRequiredMiddleware:  # pylint: disable=too-few-public-methods
    """
    Middleware to redirect users who logged in with additional hashes
    to the password reset page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user needs password reset and is authenticated
        if request.user.is_authenticated and request.session.get(
            "needs_password_reset", False
        ):

            # Allow access to the password reset page and logout
            allowed_paths = [
                reverse("authentication:force_password_reset"),
                reverse("authentication:logout"),
            ]

            if request.path not in allowed_paths:
                return redirect("authentication:force_password_reset")

        response = self.get_response(request)
        return response
