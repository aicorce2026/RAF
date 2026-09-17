from django.contrib import admin
from .models import Author, Category, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "biography")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "publication_year", "is_published", "created_at")
    list_filter = ("is_published", "category", "author")
    search_fields = ("title", "description", "author__name", "category__name")
    ordering = ("title",)
    list_select_related = ("author", "category")
    readonly_fields = ("created_at", "updated_at")
