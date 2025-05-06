from django.shortcuts import render, redirect

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