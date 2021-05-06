from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from ..authentication.models import User
from .models import College, Decision


class StudentDestinationListView(
    LoginRequiredMixin, UserPassesTestMixin, ListView
):  # pylint: disable=too-many-ancestors
    model = User
    paginate_by = 20

    def get_queryset(self):
        # Superusers can use the "all" GET parameter to see all data
        if self.request.GET.get("all", None) is not None:
            if self.request.user.is_superuser and self.request.user.is_staff:
                queryset = User.objects.all()
            else:
                raise PermissionDenied()
        else:
            queryset = User.objects.filter(publish_data=True)

        queryset = queryset.filter(is_senior=True).order_by("last_name", "first_name")

        college_id: Optional[str] = self.request.GET.get("college", None)
        if college_id is not None:
            if not college_id.isdigit():
                raise Http404()

            get_object_or_404(College, id=college_id)
            queryset = queryset.filter(decision__college__id=college_id)

        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(biography__icontains=search_query)
            )

        return queryset

    def get_context_data(
        self, *, object_list=None, **kwargs
    ):  # pylint: disable=unused-argument
        context = super().get_context_data(**kwargs)

        college_id: Optional[str] = self.request.GET.get("college", None)
        if college_id is not None:
            context["college"] = get_object_or_404(College, id=college_id)

        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            context["search_query"] = search_query

        return context

    def test_func(self):
        assert self.request.user.is_authenticated
        return self.request.user.accepted_terms

    template_name = "destinations/student_list.html"


class CollegeDestinationListView(
    LoginRequiredMixin, UserPassesTestMixin, ListView
):  # pylint: disable=too-many-ancestors
    model = College
    paginate_by = 20

    def get_queryset(self) -> QuerySet:
        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            queryset = College.objects.filter(
                Q(name__icontains=search_query)
                | Q(location__icontains=search_query)
                | Q(ceeb_code__icontains=search_query)
            )
        else:
            queryset = College.objects.all()

        queryset = (
            queryset.annotate(  # type: ignore  # mypy is annoying
                count_decisions=Count(
                    "decision", filter=Q(decision__user__publish_data=True)
                ),
                count_attending=Count(
                    "decision",
                    filter=Q(
                        decision__in=Decision.objects.filter(
                            attending_college__isnull=False
                        ),
                        decision__user__publish_data=True,
                    ),
                ),
                count_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.ADMIT,
                        decision__user__publish_data=True,
                    ),
                ),
                count_waitlist=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST,
                        decision__user__publish_data=True,
                    ),
                ),
                count_waitlist_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST_ADMIT,
                        decision__user__publish_data=True,
                    ),
                ),
                count_waitlist_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST_DENY,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_ADMIT,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_DENY,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_wl=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_wl_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL_A,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_wl_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL_D,
                        decision__user__publish_data=True,
                    ),
                ),
                count_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DENY,
                        decision__user__publish_data=True,
                    ),
                ),
            )
            .filter(count_decisions__gte=1)
            .order_by("name")
        )

        return queryset

    def get_context_data(
        self, *, object_list=None, **kwargs
    ):  # pylint: disable=unused-argument
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            context["search_query"] = search_query

        return context

    def test_func(self):
        assert self.request.user.is_authenticated
        return self.request.user.accepted_terms

    template_name = "destinations/college_list.html"
