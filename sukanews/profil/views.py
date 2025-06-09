from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from profil.models import Profile
from article.models import Article
from info.models import Info
from event.models import Event
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

def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    if username != request.user.username:
        return redirect('profil:profile', username)

    user = request.user
    filters = {
        'q': request.GET.get('q', ''),
        'sort_by': request.GET.get('sort_by', 'newest'),
    }

    articlee = list(Article.objects.filter(user__username=username))
    events = list(Event.objects.filter(author=user))
    infos = list(Info.objects.filter(author=user))

    for a in articlee:
        a.content_type = 'article'
    for e in events:
        e.content_type = 'event'
    for i in infos:
        i.content_type = 'info'

    # Gabungkan semua
    articles = articlee + events + infos

    # Filter manual (karena bukan QuerySet)
    if filters['q']:
        q = filters['q'].lower()
        articles = [
            item for item in articles
            if q in item.title.lower() or q in item.slug.lower()
        ]

    # Sort manual
    sort_key = '-updated_at' if filters['sort_by'] == 'newest' else 'updated_at'
    reverse_sort = sort_key.startswith('-')
    sort_attr = sort_key.lstrip('-')
    articles.sort(key=lambda x: getattr(x, sort_attr, None), reverse=reverse_sort)

    # Pagination
    paginator = Paginator(articles, ARTICLES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'profile': profile,
        'articles': page_obj,
        **filters,
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