from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from apps.catalog.models import Book, Author, Category

def book_list(request):
    queryset = Book.objects.filter(is_published=True).select_related('author', 'category').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    author_id = request.GET.get('author', '')

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    if category_id:
        try:
            queryset = queryset.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass

    if author_id:
        try:
            queryset = queryset.filter(author_id=int(author_id))
        except (ValueError, TypeError):
            pass

    context = {
        'books': queryset,
        'categories': Category.objects.all(),
        'authors': Author.objects.all(),
        'q': query,
        'selected_category': category_id,
        'selected_author': author_id,
    }
    return render(request, 'catalog/book_list.html', context)

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk, is_published=True)
    is_favorited = False
    if request.user.is_authenticated:
        # Import inside the view to avoid potential circular imports
        from apps.reading.models import Favorite
        is_favorited = Favorite.objects.filter(user=request.user, book=book).exists()
    return render(request, 'catalog/book_detail.html', {'book': book, 'is_favorited': is_favorited})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = author.books.filter(is_published=True).select_related('category').order_by('-created_at')
    return render(request, 'catalog/author_detail.html', {'author': author, 'books': books})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    books = category.books.filter(is_published=True).select_related('author').order_by('-created_at')
    return render(request, 'catalog/category_detail.html', {'category': category, 'books': books})
