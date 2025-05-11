from django.contrib import admin
from django.urls import path
from sukanews.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',beranda, name='beranda'),
    path('kampus/',kampus, name='kampus'),
    path('event/',event, name='event'),
    path('info/',info, name='info'),
    path('read/',detail, name='read-article'),
    path('login/',login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    path('register/',register, name='register'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
