from django.contrib import admin
from .models import ArticleNews


# Register your models here.
@admin.register(ArticleNews)
class ArticleNewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "published_at")
