from django import forms
from django.contrib.auth.models import User
from .models import Profile

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full mx-2 my-1'})
    )
    last_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full mx-2 my-1'})
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'input input-bordered w-full mx-2 my-1',
                'type': 'date'
            }
        )
    )

    class Meta:
        model = Profile
        fields = ['image', 'phone', 'website', 'description', 'about', 'birth_date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'input input-bordered w-full mx-2 my-1'}),
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full mx-2 my-1'}),
            'website': forms.URLInput(attrs={'class': 'input input-bordered w-full mx-2 my-1'}),
            'about': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full mx-2 my-1'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Ambil instance User jika tersedia
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # Isi field first_name dan last_name dengan data dari User
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            
            # Jika tanggal lahir sudah ada di Profile, isi field birth_date
            if hasattr(user.profile, 'birth_date'):
                self.fields['birth_date'].initial = user.profile.birth_date

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)

        if hasattr(profile, 'user'):
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            if commit:
                user.save()

        if commit:
            profile.save()
            
        return profile

    