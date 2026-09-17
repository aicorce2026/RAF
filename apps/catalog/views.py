from django.shortcuts import render, get_object_or_404
from apps.catalog.models import Book, Author, Category

def book_list(request):
    books = Book.objects.filter(is_published=True).select_related('author', 'category').order_by('-created_at')
    return render(request, 'catalog/book_list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk, is_published=True)
    return render(request, 'catalog/book_detail.html', {'book': book})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = author.books.filter(is_published=True).select_related('category').order_by('-created_at')
    return render(request, 'catalog/author_detail.html', {'author': author, 'books': books})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    books = category.books.filter(is_published=True).select_related('author').order_by('-created_at')
    return render(request, 'catalog/category_detail.html', {'category': category, 'books': books})
