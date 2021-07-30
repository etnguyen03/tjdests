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

    if request.user.accepted_terms:
        return redirect(reverse("authentication:index"))

    if request.method == "POST":
        form = TOSForm(request.POST)

        if form.is_valid():
            request.user.accepted_terms = form.cleaned_data.get("accept_tos")
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
