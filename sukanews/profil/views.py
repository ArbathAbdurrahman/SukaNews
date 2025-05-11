from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from profil.models import Profile
from profil.forms import ProfileForm

def profile_view(request,username):
    profile = get_object_or_404(Profile, user__username = username)
    context = {
        'profile': profile,
    }
    return render(request, 'profil.html', context)

@login_required
def edit_profile(request, username):
    # Hanya izinkan user mengedit profil mereka sendiri
    if username != request.user.username:
        return redirect('profil:profile', username=request.user.username)

    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            form.save()
            return redirect('profil:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'edit_profile.html', {'form': form})