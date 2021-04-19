import functools

from django.http import HttpRequest
from django.shortcuts import redirect


def require_accept_tos(func):
    @functools.wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated and not request.user.accepted_terms:
            return redirect("authentication:tos")

        return func(request, *args, **kwargs)

    return wrapper
