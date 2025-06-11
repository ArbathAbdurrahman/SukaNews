from django.shortcuts import render, get_object_or_404,redirect
from .models import Article, Hashtag, Category, Comment, Reply
from .forms import ArticleForm, CommentForm, ReplyForm
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

# Manage article 
ARTICLES_PER_PAGE = 20
SORT_OPTIONS = {
    'newest': '-updated_at',
    'oldest': 'updated_at',
    'most_viewed': '-views',
    'least_viewed': 'views',
}
def article(request):
    filters = {
        'q': request.GET.get('q', ''),
        'category': request.GET.get('category', ''),  # Pastikan defaultnya adalah string kosong
        'sort_by': request.GET.get('sort_by', 'newest'),
    }

    # Ambil semua kategori untuk filter
    categories = Category.objects.all()
    
    # Ambil artikel dan kaitkan dengan kategori (select_related untuk efisiensi query)
    articles = Article.objects.all().select_related('category')
    
    # Apply search filter
    if filters['q']:
        articles = articles.filter(
            Q(title__icontains=filters['q']) |
            Q(slug__icontains=filters['q']) |
            Q(description__icontains=filters['q']) |
            Q(hashtags__name__icontains=filters['q']) 
        )
    
    # Apply category filter hanya jika kategori dipilih
    if filters['category']:
        articles = articles.filter(category__name__iexact=filters['category'])
    
    # Apply sorting
    sort_field = SORT_OPTIONS.get(filters['sort_by'], '-updated_at')
    articles = articles.order_by(sort_field)
    
    # Apply distinct in case of duplicates from joins
    articles = articles.distinct()
    
    # Pagination
    paginator = Paginator(articles, ARTICLES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'articles': page_obj,
        'categories': categories,  # Menambahkan kategori untuk dropdown
        **filters,  # Menambahkan filters untuk digunakan di template
        'page_obj': page_obj,
    }
    return render(request, 'article.html', context)

def detail(request, slug):
    # Ambil artikel berdasarkan slug
    article = get_object_or_404(Article.objects.only('title', 'content', 'slug'), slug=slug)

    # Tambah jumlah views untuk profil user terkait
    if not request.session.get(f'viewed_{article.id}', False):
        article.views = models.F('views') + 1
        article.save(update_fields=['views'])
        
        # profile = article.user.profile
        # profile.views = models.F('views') + 1
        # profile.save(update_fields=['views'])

        # Tandai artikel sudah dilihat dalam session
        request.session[f'viewed_{article.id}'] = True

    # Pagination untuk related articles
    related_articles_page = request.GET.get('related_page', 1)
    related_articles = article.get_related_articles()
    related_paginator = Paginator(related_articles, 10)  # 5 related articles per halaman
    related_articles_page_obj = related_paginator.get_page(related_articles_page)

    # Komentar
    comments = article.comments.select_related('user').prefetch_related('replies__user')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.article = article
            new_comment.save()
            return redirect('article:detail', slug=slug)
    else:
        form = CommentForm()

    context = {
        'article': article,
        'comments': comments,
        'form': form,
        'related_articles': related_articles_page_obj,
    }

    return render(request, 'article_detail.html', context)

@login_required
def reply_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.comment = comment
            reply.save()
    return redirect('article:detail', slug=comment.article.slug)


# Create article
@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.author = request.user.profile.get_full_name()
            article.save()
            hashtags = form.cleaned_data['hashtags_input']
            for tag in hashtags:
                hashtag_name = tag[1:].lower()  # Hapus '#' dan simpan dalam lowercase
                hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
                article.hashtags.add(hashtag)
            
            return redirect('article:detail', slug=article.slug)
    else:
        form = ArticleForm()

    return render(request, 'article_create.html', {'form': form})

# Update article
@login_required
def update_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.user != request.user:
        return redirect('article:detail',slug=slug)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Perubahan memerlukan waktu beberapa saat")
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm(instance=article)
    return render(request,'article_create.html', {'form': form})

# Delete article
@login_required
def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.user == request.user:
        article.delete()
    return redirect('profil:profile',username=request.user.username)
