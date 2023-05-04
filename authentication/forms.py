from django import forms
from .models import CustomUser

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'password')

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6)
