from django.shortcuts import render
from .models import Book

def book_list(request):
    books = Book.objects.filter(is_published=True).select_related('author', 'category').order_by('-created_at')
    return render(request, 'catalog/book_list.html', {'books': books})
