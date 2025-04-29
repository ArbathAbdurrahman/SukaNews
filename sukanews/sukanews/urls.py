from django.contrib import admin
from django.urls import path
from sukanews.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',beranda, name='beranda'),
    path('kampus/',kampus, name='kampus'),
    path('event/',event, name='event'),
    path('info/',info, name='info'),
]
