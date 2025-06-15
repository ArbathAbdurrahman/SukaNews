from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from article.models import Article
from event.models import Event
from info.models import Info
def beranda(request):
    article = Article.objects.all().order_by('-updated_at')
    articletop = Article.objects.all().order_by('-views')
    info = Info.objects.all().order_by('-updated_at')
    event = Event.objects.all().order_by('-updated_at')
    context = {
        'articles':article,
        'articletops':articletop,
        'events': event,
        'infos': info
    }
    return render(request,'beranda.html', context)

def login_view(request):
    """View for handling user login"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.error(request, "Selamat datang " + username)
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

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

def search_page(request):
    """
    Halaman search utama dengan form pencarian dan filter
    """
    context = {
        'search_query': '',
        'selected_type': '',
        'sort_by': '',
    }
    return render(request, 'search_form.html', context)

def search_results(request):
    """
    Halaman hasil pencarian dengan hasil terpisah berdasarkan tipe
    """
    query = request.GET.get('q', '').strip()
    content_type = request.GET.get('type', 'all')
    sort_by = request.GET.get('sort', 'updated_at')
    
    # Validasi sort parameter
    valid_sorts = ['updated_at', '-updated_at', 'views', '-views', 'title', '-title']
    if sort_by not in valid_sorts:
        sort_by = '-updated_at'
    
    articles = Article.objects.none()
    events = Event.objects.none()
    infos = Info.objects.none()
    
    if query:
        # Base query untuk pencarian
        base_query = Q(title__icontains=query) | Q(description__icontains=query)
        
        if content_type == 'all' or content_type == 'article':
            articles = Article.objects.filter(base_query).select_related('user', 'category').order_by(sort_by)
        
        if content_type == 'all' or content_type == 'event':
            events = Event.objects.filter(base_query).select_related('author', 'category').order_by(sort_by)
        
        if content_type == 'all' or content_type == 'info':
            infos = Info.objects.filter(base_query).select_related('author', 'category').order_by(sort_by)
    
    # Pagination untuk setiap tipe
    articles_paginator = Paginator(articles, 6)
    events_paginator = Paginator(events, 6)
    infos_paginator = Paginator(infos, 6)
    
    page = request.GET.get('page', 1)
    
    articles_page = articles_paginator.get_page(page)
    events_page = events_paginator.get_page(page)
    infos_page = infos_paginator.get_page(page)
    
    # Hitung total hasil
    total_results = articles.count() + events.count() + infos.count()
    
    context = {
        'search_query': query,
        'selected_type': content_type,
        'sort_by': sort_by,
        'articles': articles_page,
        'events': events_page,
        'infos': infos_page,
        'total_results': total_results,
        'has_results': total_results > 0,
    }
    
    return render(request, 'search_results.html', context)

# Bahaya perlu validasi tapi malazzz
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        path = default_storage.save(f'quill_images/{image.name}', image)
        image_url = default_storage.url(path)
        return JsonResponse({'url': image_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)