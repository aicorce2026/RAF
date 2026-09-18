from django.contrib import admin
from .models import Favorite, ReadingProgress


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "book__title"]
    ordering = ["-created_at"]


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "current_page", "updated_at"]
    list_filter = ["updated_at"]
    search_fields = ["user__username", "book__title"]
    ordering = ["-updated_at"]
    readonly_fields = ["created_at", "updated_at"]
