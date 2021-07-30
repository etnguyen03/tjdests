from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.contrib.auth import password_validation


class TOSForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))

    accept_tos = forms.BooleanField(
        required=True,
        label="I have read and accept the terms of use of this website as displayed above.",
    )

    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    understand_no_reset = forms.BooleanField(
        required=True,
        label="I understand that there is NO PASSWORD RESET "
        "functionality once I no longer have access to Ion.",
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("password_confirm")

        if password1 and password1 != password2:
            raise forms.ValidationError(
                {
                    "password": [
                        "The two passwords do not match.",
                    ]
                }
            )

        if password1 is None:
            raise forms.ValidationError(
                {
                    "password": [
                        "You must provide a password.",
                    ]
                }
            )

        # Validate checkboxes checked
        accept_tos = cleaned_data.get("accept_tos")
        understand_no_reset = cleaned_data.get("understand_no_reset")

        if not accept_tos:
            raise forms.ValidationError(
                {
                    "accept_tos": [
                        "You must accept the terms of use to continue.",
                    ]
                }
            )

        if not understand_no_reset:
            raise forms.ValidationError(
                {
                    "understand_no_reset": [
                        "You must acknowledge that there is no password reset to continue.",
                    ]
                }
            )

        # Validate the password for complexity, etc.
        validators = password_validation.get_default_password_validators()
        password_validation.validate_password(password1, None, validators)

        return cleaned_data
