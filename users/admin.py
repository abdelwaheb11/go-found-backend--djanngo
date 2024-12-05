from django.contrib import admin
from .models import UserProfile
# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'desc','image', 'isActive')
    search_fields = ('user__username', 'role')
    list_filter = ('role','isActive')