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

class Event(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255,db_index=True)
    description = models.TextField(max_length=500)
    location = models.CharField(max_length=255)
    date_start = models.DateField()
    date_end = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    guidebook = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,db_index=True)
    image = models.ImageField(upload_to=user_directory_path)
    slug = models.SlugField(max_length=255, unique=True, blank=True,db_index=True)
    views = models.PositiveBigIntegerField(default=0)
    point = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    done = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    contact = models.CharField(max_length=255)
    tipe = models.CharField(max_length=20,default='Event')

    def save(self, *args, **kwargs):
        if not self.slug:  # Hanya buat slug jika belum ada
            current_time = now().strftime("%Y-%m-%d-%H%M%S")  # Format waktu
            self.slug = slugify(f"{self.title}-{current_time}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event:detail_event', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
    

# class Comment(models.Model):
#     article = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='comments')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=100)  # Nama pengguna anonim
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     likes = models.PositiveBigIntegerField(default=0)  # Menyimpan jumlah like sebagai integer
#     parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

#     def __str__(self):
#         return f'{self.article} | {self.name}'

#     class Meta:
#         ordering = ['-created_at']

# Signal untuk menghapus file gambar ketika instance dihapus
@receiver(pre_delete, sender=Event)
def delete_Event_image_on_delete(sender, instance, **kwargs):
    if instance.image and instance.image.storage.exists(instance.image.name):
        instance.image.delete(save=False)

# Signal untuk menghapus file gambar lama ketika gambar diperbarui
@receiver(pre_save, sender=Event)
def delete_old_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if the object is new
    try:
        old_instance = Event.objects.get(pk=instance.pk)
    except Event.DoesNotExist:
        return
    old_image = old_instance.image
    if old_image and old_image != instance.image and old_image.storage.exists(old_image.name):
        old_image.delete(save=False)