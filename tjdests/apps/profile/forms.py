from typing import Any, Dict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.core.exceptions import ValidationError

from tjdests.apps.authentication.models import User
from tjdests.apps.destinations.models import Decision, TestScore


class ProfilePublishForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))

        self.fields["attending_decision"].queryset = Decision.objects.filter(
            user=self.instance, admission_status__contains="ADMIT"
        )

    class Meta:
        model = User
        fields = ["publish_data", "biography", "attending_decision"]

        help_texts = {
            "biography": "ECs, intended major, advice, etc.",
        }


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ["college", "decision_type", "admission_status"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.is_edit = kwargs.pop("edit", False)
        super().__init__(*args, **kwargs)

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        # Ensure that the college is not a duplicate for this user
        # Yes, this is weird. Basically: if we are not editing
        # (i.e. creating a new one), we make sure that
        # the user does not have a Decision object with that college already.
        # If we are editing, then we ensure that the college
        # has not changed. If it has changed, then we
        # make sure that the user does not have a Decision object with that college already.
        if (
            not self.is_edit
            and Decision.objects.filter(
                user=self.request.user, college=cleaned_data.get("college")
            ).count()
            > 0
        ) or (
            self.is_edit
            and Decision.objects.filter(
                user=self.request.user,
                id=self.instance.id,
                college=cleaned_data.get("college"),
            ).count()
            != 1
            and Decision.objects.filter(
                user=self.request.user, college=cleaned_data.get("college")
            ).count()
            > 0
        ):
            raise ValidationError("You cannot add a second entry for this college")

        # Rolling and RD decisions cannot be deferred
        if cleaned_data.get("decision_type") in [Decision.REGULAR_DECISION, Decision.ROLLING]:
            if "DEFER" in cleaned_data.get("admission_status"):
                raise ValidationError("Regular Decision and Rolling decisions cannot result in a deferral")

        return cleaned_data


class TestScoreForm(forms.ModelForm):
    class Meta:
        model = TestScore
        fields = ["exam_type", "exam_score"]

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        exam_type = str(cleaned_data.get("exam_type"))

        # check if exam score is an integer
        try:
            exam_score = int(cleaned_data.get("exam_score"))  # type: ignore
        except (TypeError, ValueError):
            pass
        else:
            # ACT is 1-36
            if exam_type.startswith("ACT_"):
                if not 1 <= exam_score <= 36:
                    self.add_error("exam_score", "This is not a valid ACT exam score")

            # SAT2 and SAT EBRW/Math sections are 200-800 and mod 10
            elif exam_type.startswith("SAT2_") or cleaned_data.get("exam_type") in [
                "SAT_EBRW",
                "SAT_MATH",
            ]:
                if not 200 <= exam_score <= 800 or not exam_score % 10 == 0:
                    self.add_error(
                        "exam_score", "This is not a valid SAT section exam score"
                    )

            # SAT total is 400-1600 mod 10
            elif exam_type == "SAT_TOTAL":
                if not 400 <= exam_score <= 1600 or not exam_score % 10 == 0:
                    self.add_error("exam_score", "This is not a valid SAT exam score")

            # AP is 1-5
            elif exam_type.startswith("AP_"):
                if not 1 <= exam_score <= 5:
                    self.add_error("exam_score", "This is not a valid AP exam score")

        return cleaned_data
