# admin.py
from django.contrib import admin
from .models import Project, Investment, Commentary,Image,Favorate


class InvestmentInline(admin.TabularInline):
    model = Investment
    extra = 1


class CommentaryInline(admin.TabularInline):
    model = Commentary
    extra = 1

class ProjectImageInline(admin.TabularInline):
    model = Image
    extra = 1

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'category', 'goal_amount', 'raised_amount', 'isActive']
    search_fields = ['title', 'creator__user__username']
    list_filter = ('category',)
    inlines = [ProjectImageInline, InvestmentInline, CommentaryInline]


class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['investor', 'project', 'amount', 'created_at']
    search_fields = ['investor__user__username', 'project__title']


class CommentaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    search_fields = ['user__user__username', 'project__title']


admin.site.register(Project, ProjectAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(Commentary, CommentaryAdmin)
admin.site.register(Image)
admin.site.register(Favorate)

