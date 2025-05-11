from django.urls import path
from . import views

app_name = 'profil'

urlpatterns = [
    # path('<slug:slug>/', views.profile, name='user_detail'),
    # URL lainnya
    path('<str:username>/', views.profile_view, name='profile'),
    # path('', views.profile_view, name='profile_view'),
    path('edit/<str:username>/', views.edit_profile, name='edit_profile'),
]
