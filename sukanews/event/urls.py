from django.urls import path
from event.views import *

app_name = 'event'

urlpatterns = [
    path('',event, name='event'),
    path('create-event/',create_event, name='create_event'),
    path('update/<slug:slug>/', update_event, name='update_event'),
    path('delete/<slug:slug>/', delete_event, name='delete_event'),
    path('detail/<slug:slug>/', detail_event, name='detail_event')
]