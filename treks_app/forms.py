from django import forms
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        # Always return the email, regardless of whether it exists in the system.
        # This prevents user enumeration.
        return email