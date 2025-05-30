from django.contrib import admin

# Register your models here.
from .models import Article, Category, Hashtag

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Hashtag)