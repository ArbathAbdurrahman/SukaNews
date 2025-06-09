from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils.timezone import now
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

def user_directory_path(instance, filename):
    # File akan disimpan di MEDIA_ROOT/user_<id>/<filename>
    return f'images/user_{instance.author.id}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Info(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255,db_index=True)
    description = models.TextField(max_length=500)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,db_index=True)
    image = models.ImageField(upload_to=user_directory_path)
    slug = models.SlugField(max_length=255, unique=True, blank=True,db_index=True)
    views = models.PositiveBigIntegerField(default=0)
    point = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    done = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    contact = models.CharField(max_length=255)
    tipe = models.CharField(max_length=20,default='Pengumuman')

    def save(self, *args, **kwargs):
        if not self.slug:  # Hanya buat slug jika belum ada
            current_time = now().strftime("%Y-%m-%d-%H%M%S")  # Format waktu
            self.slug = slugify(f"{self.title}-{current_time}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('info:detail_info', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    info = models.ForeignKey(Info, on_delete=models.CASCADE, related_name='comments_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment_info')
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.info}'

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reply_comment_info')
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reply by {self.user} on comment {self.comment.id}'

# Signal untuk menghapus file gambar ketika instance dihapus
@receiver(pre_delete, sender=Info)
def delete_info_image_on_delete(sender, instance, **kwargs):
    if instance.image and instance.image.storage.exists(instance.image.name):
        instance.image.delete(save=False)

# Signal untuk menghapus file gambar lama ketika gambar diperbarui
@receiver(pre_save, sender=Info)
def delete_old_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if the object is new
    try:
        old_instance = Info.objects.get(pk=instance.pk)
    except Info.DoesNotExist:
        return
    old_image = old_instance.image
    if old_image and old_image != instance.image and old_image.storage.exists(old_image.name):
        old_image.delete(save=False)