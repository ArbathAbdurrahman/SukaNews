from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form that uses email as username
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'email'})
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'confirm password'})
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Set username to email
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that uses email instead of username
    """
    username = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'email'})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'password'})
    )