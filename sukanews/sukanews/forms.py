from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form that uses username as identifier (not email)
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'username'})
    )
    email = forms.EmailField(
        max_length=254,
        required=False,  # optional
        widget=forms.EmailInput(attrs={'placeholder': 'email (optional)'})
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
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_username(self):
        username = self.cleaned_data.get("username", "")

        # Hapus semua spasi
        username = username.replace(" ", "")

        # Validasi panjang
        if len(username) < 3:
            raise forms.ValidationError("Username must have at least 3 characters")
        elif len(username) > 30:
            raise forms.ValidationError("Username must not exceed 30 characters")

        # Konversi ke lowercase
        username = username.lower()

        # Cek apakah username sudah ada
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email



class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that uses email instead of username gajadi
    """
    username = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'username'})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'password'})
    )