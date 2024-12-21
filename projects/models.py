from django.db import models
from users.models import UserProfile
import os
import uuid

def unique_image_path(instance, filename):
    ext = filename.split('.')[-1]  
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(instance._meta.app_label, filename)


class Project(models.Model):
    Category_CHOICES = [
        ('food', 'Food'),
        ('cars', 'Cars'),
        ('art', 'Art'),
        ('musique', 'Musique'),
        ('games', 'Games'),
        ('fashion', 'Fashion'),
    ]
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects' , null=False )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=10, choices=Category_CHOICES)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    website_link = models.URLField(null=True, blank=True)
    isActive=models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Investment(models.Model):
    investor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='investments', null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='investments', null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.user.username} invested {self.amount} in {self.project.title}"


class Commentary(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments', null=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments', null=False)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=unique_image_path, null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.user.user.username} on {self.project.title}"
    
class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images') 
    image = models.ImageField(upload_to=unique_image_path, null=True, blank=True)

    def __str__(self):
        return f"Image for project: {self.project.title}"
    

class Favorate(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorate', null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='favorate', null=False)

    def __str__(self):
        return f"{self.user.user.username} favarite in {self.project.title}"


