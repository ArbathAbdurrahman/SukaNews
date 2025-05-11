from django.shortcuts import render, redirect, get_object_or_404
from profil.models import Profile

def profile_view(request,username):
    profile = get_object_or_404(Profile, user__username = username)
    context = {
        'profile': profile,
    }
    return render(request, 'profil.html', context)

def edit_profile(request):
    context = {
        'nama': 'edit_profile'
    }
    return render(request,'edit_profile.html', context)