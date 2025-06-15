from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .forms import EventForm
from .models import Event
from django.contrib import messages
from django.db.models import F
from profil.models import Profile

def event(request):
    event = Event.objects.all()
    context = {
        'events': event
    }
    return render(request,'event.html',context)

@login_required
def create_event(request):
    # Validasi user bukan organisasi
    profil = get_object_or_404(Profile, user=request.user)
    if profil.is_organization == False:
        messages.error(request, "Hanya akun organisasi yang dapat membuat event.")
        return redirect('profil:profile', request.user.username)  # Ganti dengan halaman yang sesuai untuk user biasa

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.author = request.user
            event.save()
            return redirect('event:detail_event', slug=event.slug)
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})

def detail_event(request,slug):
    event = get_object_or_404(Event.objects.filter(slug=slug))
    Event.objects.filter(pk=event.pk).update(views=F('views') + 1)
    context = {
        'event' : event
    }
    return render(request, 'detail_event.html', context)

# Update event
@login_required
def update_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if event.author != request.user:
        return redirect('event:detail_event',slug=slug)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Perubahan memerlukan waktu beberapa saat")
            return redirect(event.get_absolute_url())
    else:
        form = EventForm(instance=event)
    return render(request,'create_event.html', {'form': form})

# Delete event
@login_required
def delete_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if event.author == request.user:
        event.delete()
    return redirect('profil:profile',username=request.user.username)