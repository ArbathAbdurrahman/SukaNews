from django.contrib import admin
from django.urls import path, include
from sukanews.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',beranda, name='beranda'),
    path('login/',login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    path('register/',register, name='register'),
    path('profile/', include('profil.urls')),
    path('article/', include('article.urls')),
    path('info/', include('info.urls')),
    path('event/', include('event.urls')),
    path('upload-image/', upload_image, name='upload_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
