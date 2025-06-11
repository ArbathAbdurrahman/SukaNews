from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from info.forms import InfoForm, CommentForm, ReplyForm
from .models import Info, Comment, Reply
from django.contrib import messages
from django.db.models import F

def info(request):
    info = Info.objects.all()
    context = {
        'infos': info
    }
    return render(request, 'info.html', context)

@login_required
def create_info(request):
    if request.method == 'POST':
        form = InfoForm(request.POST, request.FILES)
        if form.is_valid():
            info = form.save(commit=False)
            info.author = request.user
            info.save()
            return redirect('info:detail_info', slug=info.slug)  # Ganti dengan nama URL tujuan 
    else:
        form = InfoForm()
    return render(request, 'create_info.html', {'form': form})

def detail_info(request,slug):
    info = get_object_or_404(Info, slug=slug)
    Info.objects.filter(pk=info.pk).update(views=F('views') + 1)

    # Komentar
    comments = info.comments_info.select_related('user').prefetch_related('replies_info')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.info = info
            new_comment.save()
            return redirect('info:detail_info', slug=slug)
    else:
        form = CommentForm()

    context = {
        'info': info,
        'comments': comments,
        'form': form,
    }
    return render(request, 'detail_info.html', context)

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
    return redirect('info:detail_info', slug=comment.info.slug)

# Update info
@login_required
def update_info(request, slug):
    info = get_object_or_404(Info, slug=slug)
    if info.author != request.user:
        return redirect('info:detail_info',slug=slug)
    if request.method == 'POST':
        form = InfoForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, "Perubahan memerlukan waktu beberapa saat")
            return redirect(info.get_absolute_url())
    else:
        form = InfoForm(instance=info)
    return render(request,'create_info.html', {'form': form})

# Delete info
@login_required
def delete_info(request, slug):
    info = get_object_or_404(Info, slug=slug)
    if info.author == request.user:
        info.delete()
    return redirect('profil:profile',username=request.user.username)