from django.shortcuts import get_object_or_404, render
from django.http import FileResponse, Http404
from django.urls import reverse
from apps.catalog.models import Book
from apps.subscriptions.decorators import active_subscription_required


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
