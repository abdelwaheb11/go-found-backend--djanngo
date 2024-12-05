from django.db import models
from django.contrib.auth.models import User
import os
import uuid


def unique_image_path(instance, filename):
    ext = filename.split('.')[-1]  # Extraire l'extension du fichier
    filename = f"{uuid.uuid4()}.{ext}"  # Générer un nom unique
    return os.path.join(instance._meta.app_label, filename)



# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('creator', 'Project Creator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    desc = models.TextField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    image = models.ImageField(upload_to=unique_image_path, null=True, blank=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"
