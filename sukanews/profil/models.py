from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def user_directory_path(instance, filename):
    # File akan disimpan di MEDIA_ROOT/user_<id>/<filename>
    return f'images/user_{instance.user.id}/profile_images_{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    description = models.CharField(max_length=255, blank=True)
    about = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def get_full_name(self):
        return f"{self.user.first_name + ' ' + self.user.last_name}"

    def __str__(self):
        return f'{self.user.username}'


# Signal untuk membuat Profile secara otomatis ketika User dibuat
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
