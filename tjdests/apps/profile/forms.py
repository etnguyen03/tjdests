from typing import Dict, Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms

from tjdests.apps.authentication.models import User
from tjdests.apps.destinations.models import Decision, TestScore


class ProfilePublishForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))

        self.fields["attending_decision"].queryset = Decision.objects.filter(
            user=self.instance,
            admission_status__in=[
                Decision.ADMIT,
                Decision.WAITLIST_ADMIT,
                Decision.DEFER_ADMIT,
            ],
        )

    class Meta:
        model = User
        fields = ["publish_data", "biography", "attending_decision"]


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ["college", "decision_type", "admission_status"]


class TestScoreForm(forms.ModelForm):
    class Meta:
        model = TestScore
        fields = ["exam_type", "exam_score"]

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        exam_score = int(cleaned_data.get("exam_score"))

        # ACT is 1-36
        if cleaned_data.get("exam_type").startswith("ACT_"):
            if not 1 <= exam_score <= 36:
                self.add_error("exam_score", "This is not a valid ACT exam score")

        # SAT2 and SAT EBRW/Math sections are 200-800 and mod 10
        elif cleaned_data.get("exam_type").startswith("SAT2_") or cleaned_data.get("exam_type") in ["SAT_EBRW", "SAT_MATH"]:
            if not 200 <= exam_score <= 800 or not exam_score % 10 == 0:
                self.add_error("exam_score", "This is not a valid SAT section exam score")

        # SAT total is 400-1600 mod 10
        elif cleaned_data.get("exam_type") == "SAT_TOTAL":
            if not 400 <= exam_score <= 1600 or not exam_score % 10 == 0:
                self.add_error("exam_score", "This is not a valid SAT exam score")

        # AP is 1-5
        if cleaned_data.get("exam_type").startswith("AP_"):
            if not 1 <= exam_score <= 36:
                self.add_error("exam_score", "This is not a valid AP exam score")

        return cleaned_data

