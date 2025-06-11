from django.urls import path
from info.views import *

app_name = 'info'

urlpatterns = [
    path('', info, name='info'),
    path('create_info/', create_info, name='create_info'),
    path('detail-info/<slug:slug>/', detail_info, name='detail_info'),
    path('update/<slug:slug>/', update_info, name='update_info'),
    path('delete/<slug:slug>/', delete_info, name='delete_info'),
    path('comment/<int:comment_id>/reply/', reply_comment, name='reply_comment'),
]