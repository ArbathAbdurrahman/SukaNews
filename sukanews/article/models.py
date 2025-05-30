from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils.timezone import now
from itertools import chain
from random import sample
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

def user_directory_path(instance, filename):
    # File akan disimpan di MEDIA_ROOT/user_<id>/<filename>
    return f'images/user_{instance.user.id}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"#{self.name}"

class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255,db_index=True)
    description = models.TextField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles',db_index=True)
    image = models.ImageField(upload_to=user_directory_path)
    slug = models.SlugField(max_length=255, unique=True, blank=True,db_index=True)
    content = models.TextField()
    hashtags = models.ManyToManyField(Hashtag, related_name='articles',db_index=True)
    views = models.PositiveBigIntegerField(default=0)
    tipe = models.CharField(max_length=20,default='Artikel')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Hanya buat slug jika belum ada
            current_time = now().strftime("%Y-%m-%d-%H%M%S")  # Format waktu
            self.slug = slugify(f"{self.title}-{current_time}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article:detail', kwargs={'slug': self.slug})

    def get_related_articles(self):
        # Ambil artikel dengan kategori yang sama, tetapi bukan artikel ini
        category_related = Article.objects.filter(
            category=self.category
        ).exclude(id=self.id).only('title', 'slug', 'image')
        
        # Ambil artikel dengan hashtag yang sama, tetapi bukan artikel ini
        hashtag_related = Article.objects.filter(
            hashtags__in=self.hashtags.all()
        ).exclude(id=self.id).only('title', 'slug', 'image')
        
        # Gabungkan kedua queryset tanpa duplikasi
        combined_related = list(chain(category_related, hashtag_related))
        
        # Menggunakan set untuk memastikan tidak ada duplikasi artikel berdasarkan ID
        unique_related_articles = {article.id: article for article in combined_related}.values()
        
        # Pilih hingga 10 artikel secara acak
        related_articles = sample(list(unique_related_articles), min(len(unique_related_articles), 10))
        
        return related_articles


    def __str__(self):
        return self.title
    
class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.article}'

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reply by {self.user} on comment {self.comment.id}'

    
# Signal untuk menghapus file gambar ketika instance dihapus
@receiver(pre_delete, sender=Article)
def delete_article_image_on_delete(sender, instance, **kwargs):
    if instance.image and instance.image.storage.exists(instance.image.name):
        instance.image.delete(save=False)

# Signal untuk menghapus file gambar lama ketika gambar diperbarui
@receiver(pre_save, sender=Article)
def delete_old_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if the object is new
    try:
        old_instance = Article.objects.get(pk=instance.pk)
    except Article.DoesNotExist:
        return
    old_image = old_instance.image
    if old_image and old_image != instance.image and old_image.storage.exists(old_image.name):
        old_image.delete(save=False)