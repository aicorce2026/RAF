import os
import tempfile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from apps.catalog.models import Author, Category, Book
from apps.subscriptions.models import SubscriptionRequest, Subscription


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username, password='testpass123'):
    return User.objects.create_user(username=username, password=password)


def make_book(title='Test Book', has_pdf=True):
    author, _ = Author.objects.get_or_create(name='Test Author')
    category, _ = Category.objects.get_or_create(name='Test Category')
    book = Book(
        title=title,
        author=author,
        category=category,
        is_published=True,
    )
    if has_pdf:
        book.pdf_file = SimpleUploadedFile(
            'test.pdf', b'%PDF-1.4 fake content', content_type='application/pdf'
        )
    book.save()
    return book


def make_active_subscription(user):
    req = SubscriptionRequest.objects.create(
        user=user,
        payment_method='bank_transfer',
        receipt_file='subscriptions/receipts/test.pdf',
        status=SubscriptionRequest.Status.APPROVED,
    )
    now = timezone.now()
    return Subscription.objects.create(
        user=user,
        request=req,
        start_at=now - timedelta(days=1),
        end_at=now + timedelta(days=29),
    )


def make_expired_subscription(user):
    req = SubscriptionRequest.objects.create(
        user=user,
        payment_method='bank_transfer',
        receipt_file='subscriptions/receipts/r2.pdf',
        status=SubscriptionRequest.Status.APPROVED,
    )
    now = timezone.now()
    return Subscription.objects.create(
        user=user,
        request=req,
        start_at=now - timedelta(days=60),
        end_at=now - timedelta(days=30),
    )


def make_future_subscription(user):
    req = SubscriptionRequest.objects.create(
        user=user,
        payment_method='bank_transfer',
        receipt_file='subscriptions/receipts/r3.pdf',
        status=SubscriptionRequest.Status.APPROVED,
    )
    now = timezone.now()
    return Subscription.objects.create(
        user=user,
        request=req,
        start_at=now + timedelta(days=5),
        end_at=now + timedelta(days=35),
    )


# ---------------------------------------------------------------------------
# Reader page tests
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReaderPageTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('reader_user')
        self.book = make_book()
        self.reader_url = reverse('reading:reader', args=[self.book.pk])

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.reader_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_authenticated_user_without_subscription_denied(self):
        self.client.login(username='reader_user', password='testpass123')
        response = self.client.get(self.reader_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/subscriptions/', response['Location'])

    def test_expired_subscription_denied(self):
        make_expired_subscription(self.user)
        self.client.login(username='reader_user', password='testpass123')
        response = self.client.get(self.reader_url)
        self.assertEqual(response.status_code, 302)

    def test_future_subscription_denied(self):
        make_future_subscription(self.user)
        self.client.login(username='reader_user', password='testpass123')
        response = self.client.get(self.reader_url)
        self.assertEqual(response.status_code, 302)

    def test_active_subscriber_gets_reader_200(self):
        make_active_subscription(self.user)
        self.client.login(username='reader_user', password='testpass123')
        response = self.client.get(self.reader_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading/reader.html')

    def test_unpublished_book_returns_404_for_active_subscriber(self):
        make_active_subscription(self.user)
        self.book.is_published = False
        self.book.save()
        self.client.login(username='reader_user', password='testpass123')
        response = self.client.get(self.reader_url)
        self.assertEqual(response.status_code, 404)

    def test_book_without_pdf_returns_404(self):
        book_no_pdf = make_book(title='No PDF Book', has_pdf=False)
        make_active_subscription(self.user)
        self.client.login(username='reader_user', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[book_no_pdf.pk]))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Protected PDF endpoint tests
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProtectedPdfEndpointTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('pdf_user')
        self.book = make_book()
        self.pdf_url = reverse('reading:pdf_file', args=[self.book.pk])

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_anonymous_cannot_fetch_pdf(self):
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_non_subscriber_cannot_fetch_pdf(self):
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 302)

    def test_expired_subscriber_cannot_fetch_pdf(self):
        make_expired_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 302)

    def test_future_subscriber_cannot_fetch_pdf(self):
        make_future_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 302)

    def test_active_subscriber_receives_pdf(self):
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 200)

    def test_response_content_type_is_pdf(self):
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_response_is_inline_not_attachment(self):
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertIn('inline', response['Content-Disposition'])
        self.assertNotIn('attachment', response['Content-Disposition'])

    def test_response_does_not_reveal_filesystem_path(self):
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        disposition = response.get('Content-Disposition', '')
        self.assertNotIn('books/pdfs/', disposition)
        self.assertNotIn('media', disposition)

    def test_unpublished_book_pdf_cannot_be_fetched(self):
        self.book.is_published = False
        self.book.save()
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 404)

    def test_missing_pdf_file_returns_404(self):
        book_no_pdf = make_book(title='No PDF', has_pdf=False)
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(reverse('reading:pdf_file', args=[book_no_pdf.pk]))
        self.assertEqual(response.status_code, 404)

    def test_security_headers_present(self):
        make_active_subscription(self.user)
        self.client.login(username='pdf_user', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('no-store', response['Cache-Control'])


# ---------------------------------------------------------------------------
# Template security tests
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReaderTemplateSecurityTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('tmpl_user')
        self.book = make_book()

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_reader_template_does_not_contain_pdf_file_url(self):
        make_active_subscription(self.user)
        self.client.login(username='tmpl_user', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        content = response.content.decode()
        self.assertNotIn('books/pdfs/', content)
        self.assertNotIn('/media/', content)

    def test_reader_uses_protected_django_endpoint(self):
        make_active_subscription(self.user)
        self.client.login(username='tmpl_user', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        content = response.content.decode()
        expected = reverse('reading:pdf_file', args=[self.book.pk])
        self.assertIn(expected, content)

    def test_book_detail_does_not_expose_pdf_url(self):
        response = self.client.get(reverse('catalog:book_detail', args=[self.book.pk]))
        content = response.content.decode()
        self.assertNotIn('books/pdfs/', content)
        self.assertNotIn('/media/', content)


# ---------------------------------------------------------------------------
# Media bypass interception test
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class MediaBypassProtectionTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('bypass_user')
        self.book = make_book()

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_direct_media_book_pdf_url_is_blocked(self):
        # Attempt to access the book PDF directly via the media URL
        filename = os.path.basename(self.book.pdf_file.name)
        direct_url = f'/media/books/pdfs/{filename}'
        response = self.client.get(direct_url)
        # Must be blocked — 403 Forbidden, never 200
        self.assertEqual(response.status_code, 403)

    def test_direct_media_book_pdf_blocked_even_for_subscriber(self):
        make_active_subscription(self.user)
        self.client.login(username='bypass_user', password='testpass123')
        filename = os.path.basename(self.book.pdf_file.name)
        direct_url = f'/media/books/pdfs/{filename}'
        response = self.client.get(direct_url)
        self.assertEqual(response.status_code, 403)


# ---------------------------------------------------------------------------
# Regression: public catalog pages remain public
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PublicCatalogRegressionTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.book = make_book()

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_home_remains_publicly_accessible(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_book_list_remains_publicly_accessible(self):
        response = self.client.get(reverse('catalog:book_list'))
        self.assertEqual(response.status_code, 200)

    def test_book_detail_remains_publicly_accessible(self):
        response = self.client.get(reverse('catalog:book_detail', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
