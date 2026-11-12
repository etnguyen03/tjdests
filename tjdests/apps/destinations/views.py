from typing import List, Optional

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView

from ..authentication.models import User
from .models import College, Decision


def get_current_academic_year() -> int:
    """Get the current academic year."""
    now = timezone.now()
    current_year = now.year
    if now.month >= 8:  # Aug-Dec
        return current_year + 1
    else:  # Jan-Jul
        return current_year


def get_available_graduation_years() -> List[int]:
    """Get list of available graduation years from published user data."""
    current_year = get_current_academic_year()

    years = (
        User.objects.filter(publish_data=True, graduation_year__gt=0)
        .values_list("graduation_year", flat=True)
        .distinct()
        .order_by("-graduation_year")
    )

    years_list = list(years)

    # Ensure current senior class is always included as first option
    if current_year not in years_list:
        years_list.insert(0, current_year)
    else:
        # Move current year to first position if it's not already there
        years_list.remove(current_year)
        years_list.insert(0, current_year)

    return years_list


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

        # Filter by graduation year
        graduation_year = self.request.GET.get("year", None)
        if graduation_year is not None:
            if not graduation_year.isdigit() or int(graduation_year) == 0:
                raise Http404()
            queryset = queryset.filter(graduation_year=int(graduation_year))
        else:
            # Default to current academic year
            current_academic_year = get_current_academic_year()
            queryset = queryset.filter(graduation_year=current_academic_year)

        queryset = queryset.order_by("last_name", "preferred_name").prefetch_related(
            "testscore_set"
        )

        college_id: Optional[str] = self.request.GET.get("college", None)
        if college_id is not None:
            if not college_id.isdigit():
                raise Http404()

            get_object_or_404(College, id=college_id)
            queryset = queryset.filter(decision__college__id=college_id)

        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            queryset = queryset.filter(
                Q(  # pylint: disable=unsupported-binary-operation
                    first_name__icontains=search_query
                )
                | Q(last_name__icontains=search_query)
                | Q(nickname__icontains=search_query)
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

        # Add graduation year context
        graduation_year = self.request.GET.get("year", None)
        if graduation_year is not None:
            context["selected_year"] = int(graduation_year)
        else:
            context["selected_year"] = get_current_academic_year()

        context["available_years"] = get_available_graduation_years()
        context["current_academic_year"] = get_current_academic_year()

        return context

    def test_func(self):
        assert self.request.user.is_authenticated
        return self.request.user.accepted_terms and not self.request.user.is_banned

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
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )
        else:
            queryset = College.objects.all()

        # Get graduation year filter
        graduation_year = self.request.GET.get("year", None)
        if graduation_year is not None:
            if not graduation_year.isdigit() or int(graduation_year) == 0:
                raise Http404()
            year_filter = Q(decision__user__graduation_year=int(graduation_year))
        else:
            # Default to current academic year
            current_academic_year = get_current_academic_year()
            year_filter = Q(decision__user__graduation_year=current_academic_year)

        queryset = (
            queryset.annotate(  # type: ignore  # mypy is annoying
                count_decisions=Count(
                    "decision",
                    filter=Q(decision__user__publish_data=True) & year_filter,
                ),
                count_attending=Count(
                    "decision",
                    filter=Q(
                        decision__in=Decision.objects.filter(
                            attending_college__isnull=False
                        ),
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.ADMIT,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_waitlist=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_waitlist_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST_ADMIT,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_waitlist_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST_DENY,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_defer=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_defer_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_ADMIT,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_defer_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_DENY,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_defer_wl=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_defer_wl_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL_A,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_defer_wl_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL_D,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
                ),
                count_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DENY,
                        decision__user__publish_data=True,
                    )
                    & year_filter,
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

        # Add graduation year context
        graduation_year = self.request.GET.get("year", None)
        if graduation_year is not None:
            context["selected_year"] = int(graduation_year)
        else:
            context["selected_year"] = get_current_academic_year()

        context["available_years"] = get_available_graduation_years()
        context["current_academic_year"] = get_current_academic_year()

        return context

    def test_func(self):
        assert self.request.user.is_authenticated
        return self.request.user.accepted_terms and not self.request.user.is_banned

    template_name = "destinations/college_list.html"
