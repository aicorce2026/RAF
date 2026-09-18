from django.shortcuts import get_object_or_404, render, redirect
from django.http import FileResponse, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.catalog.models import Book
from apps.subscriptions.decorators import active_subscription_required
from .models import Favorite

@active_subscription_required
def reader(request, pk):
    """Protected PDF reader page. Requires authentication and an active subscription."""
    book = get_object_or_404(Book, pk=pk, is_published=True)
    if not book.pdf_file:
        raise Http404("هذا الكتاب لا يحتوي على ملف PDF.")
    protected_pdf_url = reverse("reading:pdf_file", args=[book.pk])
    return render(
        request,
        'reading/reader.html',
        {
            'book': book,
            'protected_pdf_url': protected_pdf_url,
        }
    )


@active_subscription_required
def pdf_file(request, pk):
    """
    Protected PDF streaming endpoint.
    Streams the book PDF only to authenticated users with an active subscription.
    Never discloses the physical filesystem path.
    """
    book = get_object_or_404(Book, pk=pk, is_published=True)
    if not book.pdf_file:
        raise Http404("لا يوجد ملف PDF لهذا الكتاب.")
    try:
        pdf = book.pdf_file.open('rb')
    except (FileNotFoundError, OSError):
        raise Http404("ملف PDF غير موجود على الخادم.")
    response = FileResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="book-{book.pk}.pdf"'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    return response


@login_required
@require_POST
def favorite_toggle(request, book_pk):
    """
    Toggle a published book in the user's favorites.
    """
    book = get_object_or_404(Book, pk=book_pk, is_published=True)
    favorite = Favorite.objects.filter(user=request.user, book=book).first()

    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(user=request.user, book=book)

    next_url = request.POST.get('next')
    # Extremely basic safe redirect to local paths only
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)
    return redirect('catalog:book_detail', pk=book.pk)


@login_required
def favorite_list(request):
    """
    List the logged-in user's favorites.
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('book', 'book__author', 'book__category')
    return render(request, 'reading/favorite_list.html', {'favorites': favorites})
