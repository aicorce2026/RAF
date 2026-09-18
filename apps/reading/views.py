from django.shortcuts import get_object_or_404, render, redirect
from django.http import FileResponse, Http404, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.catalog.models import Book
from apps.subscriptions.decorators import active_subscription_required
from apps.subscriptions.services import get_active_subscription
from .models import Favorite, ReadingProgress


@active_subscription_required
def reader(request, pk):
    """
    Protected PDF reader page. Requires authentication and an active subscription.
    Loads the user's last saved page so reading can resume from where they left off.
    """
    book = get_object_or_404(Book, pk=pk, is_published=True)
    if not book.pdf_file:
        raise Http404("هذا الكتاب لا يحتوي على ملف PDF.")
    protected_pdf_url = reverse("reading:pdf_file", args=[book.pk])

    # Retrieve the saved reading progress for this user and book, if it exists.
    # Do NOT create a record here — only create/update when the user actually navigates pages.
    progress = ReadingProgress.objects.filter(user=request.user, book=book).first()
    initial_page = progress.current_page if progress else 1

    return render(
        request,
        'reading/reader.html',
        {
            'book': book,
            'protected_pdf_url': protected_pdf_url,
            'initial_page': initial_page,
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


@active_subscription_required
@require_POST
def progress_update(request, pk):
    """
    Protected POST-only endpoint to save reading progress.

    Accepts a page number in POST data and creates or updates the ReadingProgress
    record for request.user + book. Ownership is always derived from request.user —
    client-supplied user identifiers are never accepted.

    Returns JSON: {"ok": true, "current_page": <number>}
    Returns 400 for invalid page values.
    Returns 404 for non-existent or unpublished books.
    """
    book = get_object_or_404(Book, pk=pk, is_published=True)

    # Server-side page validation — never trust the client alone.
    raw_page = request.POST.get('page')
    if raw_page is None:
        return JsonResponse({"ok": False, "error": "رقم الصفحة مطلوب."}, status=400)

    try:
        page = int(raw_page)
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "رقم الصفحة يجب أن يكون عدداً صحيحاً."}, status=400)

    if page < 1:
        return JsonResponse({"ok": False, "error": "رقم الصفحة يجب أن يكون 1 أو أكبر."}, status=400)

    # Use get_or_create to avoid duplicate records, then update the page.
    progress, _created = ReadingProgress.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={"current_page": page},
    )
    if not _created:
        # Record already existed — update the page only if it actually changed.
        if progress.current_page != page:
            progress.current_page = page
            progress.save(update_fields=["current_page", "updated_at"])

    return JsonResponse({"ok": True, "current_page": progress.current_page})


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


@login_required
def my_library(request):
    """Display the authenticated user's published personal-library items."""
    reading_progress = ReadingProgress.objects.filter(
        user=request.user,
        book__is_published=True,
    ).select_related(
        "book",
        "book__author",
        "book__category",
    ).order_by("-updated_at")

    favorites = Favorite.objects.filter(
        user=request.user,
        book__is_published=True,
    ).select_related(
        "book",
        "book__author",
        "book__category",
    ).order_by("-created_at")

    context = {
        "reading_progress": reading_progress,
        "favorites": favorites,
        "active_subscription": get_active_subscription(request.user),
    }
    return render(request, "reading/my_library.html", context)
