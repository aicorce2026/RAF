from django.shortcuts import render
from apps.catalog.models import Book

def home(request):
    published_books = (
        Book.objects
        .filter(is_published=True)
        .select_related("author", "category")
        .order_by("-created_at")[:6]
    )
    return render(request, "core/home.html", {'published_books': published_books})
