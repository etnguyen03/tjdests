from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms

from tjdests.apps.authentication.models import User
from tjdests.apps.destinations.models import Decision


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
