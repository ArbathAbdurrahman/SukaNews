from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
def beranda(request):
    context = {
        'nama': 'Suka News'
    }
    return render(request,'beranda.html', context)
def kampus(request):
    context = {
        'nama': 'Kampus'
    }
    return render(request,'kampus.html', context)
def event(request):
    context = {
        'nama': 'Event'
    }
    return render(request,'event.html', context)
def info(request):
    context = {
        'nama': 'Info'
    }
    return render(request,'info.html', context)
def acara(request):
    context = {
        'nama': 'acara'
    }
    return render(request,'acara.html', context)
def detail(request):
    context = {
        'nama': 'detail'
    }
    return render(request,'detail.html', context)

def login_view(request):
    """View for handling user login"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('beranda')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def register(request):
    """View for handling user registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('beranda')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    """View for handling user logout"""
    logout(request)
    return redirect('login')