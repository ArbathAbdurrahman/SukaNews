from django.urls import path, include
from . import views

app_name = 'article'

urlpatterns = [
    path('', views.article, name='article'),
    path('read/<slug:slug>/', views.detail, name='detail'),
    path('update/<slug:slug>/', views.update_article, name='update_article'),
    path('delete/<slug:slug>/', views.delete_article, name='delete_article'),
    path('create/', views.create_article, name='create'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
]