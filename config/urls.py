"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')\
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponseForbidden
from django.conf import settings
from django.conf.urls.static import static


def _blocked_book_pdf(request, path):
    """
    Block direct access to book PDF media files.
    All book PDF access must go through the protected reading:pdf_file endpoint.
    This view intercepts /media/books/pdfs/... before Django's dev media server.
    """
    return HttpResponseForbidden(
        "الوصول المباشر لملفات الكتب غير مسموح. يرجى استخدام قارئ الكتاب.",
        content_type="text/plain; charset=utf-8",
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('books/', include('apps.catalog.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),
    path('reading/', include('apps.reading.urls')),
    # Block direct media access to book PDFs — MUST come before media static() serving
    re_path(r'^media/books/pdfs/(?P<path>.+)$', _blocked_book_pdf),
    
    # Protect subscription receipts
    re_path(r'^media/subscriptions/receipts/(?P<path>.+)$', __import__('apps.subscriptions.views', fromlist=['protected_receipt_file']).protected_receipt_file),
]

# Dev media serving for all other media (receipts served only via admin, not public templates)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
