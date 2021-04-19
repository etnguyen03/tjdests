from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from ..authentication.models import User
from .models import College, Decision


class StudentDestinationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.filter(publish_data=True, is_senior=True).order_by(
            "last_name", "first_name"
        )

        college_id = self.request.GET.get("college", None)
        if college_id is not None:
            get_object_or_404(College, id=college_id)
            queryset = queryset.filter(decision__college__id=college_id)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StudentDestinationListView,
                        self).get_context_data(**kwargs)

        college_id = self.request.GET.get("college", None)
        if college_id is not None:
            context["college"] = get_object_or_404(College, id=college_id)

        return context

    def test_func(self):
        return self.request.user.accepted_terms

    template_name = "destinations/student_list.html"


class CollegeDestinationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = College
    paginate_by = 20
    queryset = (
        College.objects.annotate(
            count_decisions=Count(
                "decision", filter=Q(decision__user__publish_data=True)
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

    def test_func(self):
        return self.request.user.accepted_terms

    template_name = "destinations/college_list.html"
