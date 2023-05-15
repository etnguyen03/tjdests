from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from tjdests.apps.authentication.forms import TOSForm


class IndexView(TemplateView):
    template_name = "authentication/index.html"


@login_required
def accept_tos_view(request: HttpRequest) -> HttpResponse:
    assert request.user.is_authenticated

    if settings.LOGIN_LOCKED:
        if not request.user.is_superuser:
            logout(request)
            messages.error(request, "Login is restricted to administrators only.")
            return redirect(reverse("authentication:index"))

    if not request.user.is_student:
        logout(request)
        messages.error(request, "You must be a student to access this site.")
        return redirect(reverse("authentication:index"))

    if request.user.is_banned:
        logout(request)
        messages.error(
            request,
            "You have been banned from this site. "
            "Contact the site's administrator to appeal your ban.",
        )
        return redirect(reverse("authentication:index"))

    if request.user.accepted_terms:
        return redirect(reverse("authentication:index"))

    if request.method == "POST":
        form = TOSForm(request.POST)

        if form.is_valid():
            accept_tos = form.cleaned_data.get("accept_tos")  # type: ignore
            request.user.accepted_terms = accept_tos  # type: ignore
            request.user.set_password(form.cleaned_data.get("password"))
            request.user.save()

            login(
                request,
                request.user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            messages.success(request, "You have logged in.")

            return redirect(reverse("authentication:index"))
    else:
        form = TOSForm()

    context = {"form": form}

    return render(request, "authentication/accept_tos.html", context=context)


def lockout(request, *args, **kwargs):
    return HttpResponse(
        (
            "Your account has been locked due to too many failed login attempts, ",
            f"please contact {settings.MAINTAINER} for assistance ",
            "<i>or remember your password next time!</i>",
        ),
        status=403,
    )
