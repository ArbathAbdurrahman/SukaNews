from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from profil.models import Profile
from article.models import Article
from profil.forms import ProfileForm
from django.db.models import Q
from django.core.paginator import Paginator

ARTICLES_PER_PAGE = 20
SORT_OPTIONS = {
    'newest': '-updated_at',
    'oldest': 'updated_at',
    'most_viewed': '-views',
    'least_viewed': 'views',
}

def profile_view(request,username):
    profile = get_object_or_404(Profile, user__username = username)
    if username != request.user.username:
        return redirect('profil:profile',username)
    # Get filter parameters with defaults
    filters = {
        'q': request.GET.get('q', ''),
        'sort_by': request.GET.get('sort_by', 'newest'),
    }

    articles = Article.objects.filter(user__username=username)
    
    # Apply search filter
    if filters['q']:
        articles = articles.filter(
            Q(title__icontains=filters['q']) |
            Q(slug__icontains=filters['q'])
        )

    # Apply sorting
    sort_field = SORT_OPTIONS.get(filters['sort_by'], '-updated_at')
    articles = articles.order_by(sort_field)
    
    # Apply distinct in case of duplicates from joins
    articles = articles.distinct()
    
    # Pagination
    paginator = Paginator(articles, ARTICLES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'profile': profile,
        'articles': page_obj,
        **filters,  # Unpack filters into context
        'page_obj': page_obj,
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