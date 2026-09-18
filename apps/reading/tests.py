import os
import tempfile
from django.test import TestCase, Client, override_settings
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from apps.catalog.models import Author, Category, Book
from apps.subscriptions.models import SubscriptionRequest, Subscription
from apps.reading.models import Favorite, ReadingProgress
from django.db import IntegrityError

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


# ---------------------------------------------------------------------------
# Favorite Model Tests
# ---------------------------------------------------------------------------

class FavoriteModelTests(TestCase):

    def setUp(self):
        self.user1 = make_user('user1')
        self.user2 = make_user('user2')
        self.book1 = make_book('Book 1')
        self.book2 = make_book('Book 2')

    def test_favorite_can_be_created(self):
        fav = Favorite.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertEqual(fav.user, self.user1)
        self.assertEqual(fav.book, self.book1)

    def test_user_relationship_works(self):
        fav = Favorite.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(self.user1.favorites.count(), 1)
        self.assertEqual(self.user1.favorites.first(), fav)

    def test_book_relationship_works(self):
        fav = Favorite.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(self.book1.favorited_by.count(), 1)
        self.assertEqual(self.book1.favorited_by.first(), fav)

    def test_duplicate_favorite_rejected(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=self.user1, book=self.book1)

    def test_different_users_can_favorite_same_book(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        Favorite.objects.create(user=self.user2, book=self.book1)
        self.assertEqual(Favorite.objects.count(), 2)

    def test_same_user_can_favorite_different_books(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        Favorite.objects.create(user=self.user1, book=self.book2)
        self.assertEqual(Favorite.objects.count(), 2)

    def test_str_representation(self):
        fav = Favorite.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(str(fav), f"{self.user1.username} - {self.book1.title}")


# ---------------------------------------------------------------------------
# Favorite Toggle Tests
# ---------------------------------------------------------------------------

class FavoriteToggleTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('toggle_user')
        self.book = make_book()
        self.toggle_url = reverse('reading:favorite_toggle', args=[self.book.pk])

    def test_anonymous_user_cannot_toggle(self):
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_get_cannot_modify_state(self):
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.get(self.toggle_url)
        # Should be 405 Method Not Allowed due to @require_POST
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_authenticated_post_adds_favorite(self):
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertEqual(Favorite.objects.first().user, self.user)

    def test_second_post_removes_favorite(self):
        self.client.login(username='toggle_user', password='testpass123')
        Favorite.objects.create(user=self.user, book=self.book)
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_unpublished_book_cannot_be_favorited(self):
        self.book.is_published = False
        self.book.save()
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_book_returns_404(self):
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.post(reverse('reading:favorite_toggle', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_safe_redirect_works(self):
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.post(self.toggle_url, {'next': '/some/local/path/'})
        self.assertRedirects(response, '/some/local/path/', fetch_redirect_response=False)

    def test_unsafe_redirect_falls_back(self):
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.post(self.toggle_url, {'next': 'http://evil.com'})
        expected_url = reverse('catalog:book_detail', args=[self.book.pk])
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_protocol_relative_redirect_falls_back(self):
        self.client.login(username='toggle_user', password='testpass123')
        response = self.client.post(self.toggle_url, {'next': '//evil.com/path'})
        expected_url = reverse('catalog:book_detail', args=[self.book.pk])
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_favorite_toggle_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        response = csrf_client.post(self.toggle_url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Favorite.objects.exists())

    def test_post_cannot_forge_another_users_favorite_ownership(self):
        other_user = make_user('other_user')
        self.client.login(username='toggle_user', password='testpass123')
        # Attempt to forge user id in post data
        response = self.client.post(self.toggle_url, {'user': other_user.pk, 'user_id': other_user.pk})
        self.assertEqual(response.status_code, 302)
        # Verify the created favorite belongs to the logged-in user, NOT the other_user
        fav = Favorite.objects.first()
        self.assertEqual(fav.user, self.user)
        self.assertNotEqual(fav.user, other_user)


# ---------------------------------------------------------------------------
# Favorite List Tests & Integration
# ---------------------------------------------------------------------------

class FavoriteListTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = make_user('user1')
        self.user2 = make_user('user2')
        self.book1 = make_book('Book 1')
        self.book2 = make_book('Book 2')
        self.list_url = reverse('reading:favorite_list')

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_authenticated_can_view_list(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_list_shows_only_own_favorites(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        Favorite.objects.create(user=self.user2, book=self.book2)

        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'Book 1')
        self.assertNotContains(response, 'Book 2')

    def test_unpublished_favorite_is_hidden(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        self.book1.is_published = False
        self.book1.save(update_fields=['is_published'])

        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)

        self.assertNotContains(response, self.book1.title)

    def test_empty_list_shows_arabic_state(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'لا توجد كتب في المفضلة حالياً')

    def test_book_detail_shows_add_favorite_for_unfavorited(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('catalog:book_detail', args=[self.book1.pk]))
        self.assertContains(response, 'إضافة إلى المفضلة')
        self.assertNotContains(response, 'إزالة من المفضلة')

    def test_book_detail_shows_remove_favorite_when_favorited(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('catalog:book_detail', args=[self.book1.pk]))
        self.assertContains(response, 'إزالة من المفضلة')
        self.assertNotContains(response, 'إضافة إلى المفضلة')

    def test_csrf_token_present_in_book_detail(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('catalog:book_detail', args=[self.book1.pk]))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_no_pdf_url_exposed_in_favorites_list(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertNotIn('books/pdfs/', response.content.decode())

    def test_no_receipt_url_exposed_in_favorites_list(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertNotIn('subscriptions/receipts/', response.content.decode())

    def test_list_contains_link_to_favorite_book_detail(self):
        Favorite.objects.create(user=self.user1, book=self.book1)
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(self.list_url)
        expected_url = reverse('catalog:book_detail', args=[self.book1.pk])
        self.assertContains(response, expected_url)


# ---------------------------------------------------------------------------
# ReadingProgress Model Tests
# ---------------------------------------------------------------------------

class ReadingProgressModelTests(TestCase):

    def setUp(self):
        self.user1 = make_user('rp_user1')
        self.user2 = make_user('rp_user2')
        self.book1 = make_book('RP Book 1')
        self.book2 = make_book('RP Book 2')

    def test_reading_progress_can_be_created(self):
        rp = ReadingProgress.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(ReadingProgress.objects.count(), 1)
        self.assertEqual(rp.user, self.user1)
        self.assertEqual(rp.book, self.book1)

    def test_default_current_page_is_1(self):
        rp = ReadingProgress.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(rp.current_page, 1)

    def test_user_relationship_works(self):
        rp = ReadingProgress.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(self.user1.reading_progress.count(), 1)
        self.assertEqual(self.user1.reading_progress.first(), rp)

    def test_book_relationship_works(self):
        rp = ReadingProgress.objects.create(user=self.user1, book=self.book1)
        self.assertEqual(self.book1.reading_progress.count(), 1)
        self.assertEqual(self.book1.reading_progress.first(), rp)

    def test_same_user_book_cannot_have_duplicate_progress(self):
        ReadingProgress.objects.create(user=self.user1, book=self.book1)
        with self.assertRaises(IntegrityError):
            ReadingProgress.objects.create(user=self.user1, book=self.book1)

    def test_different_users_can_have_progress_for_same_book(self):
        ReadingProgress.objects.create(user=self.user1, book=self.book1)
        ReadingProgress.objects.create(user=self.user2, book=self.book1)
        self.assertEqual(ReadingProgress.objects.count(), 2)

    def test_same_user_can_have_progress_for_different_books(self):
        ReadingProgress.objects.create(user=self.user1, book=self.book1)
        ReadingProgress.objects.create(user=self.user1, book=self.book2)
        self.assertEqual(ReadingProgress.objects.count(), 2)

    def test_current_page_can_be_updated(self):
        rp = ReadingProgress.objects.create(user=self.user1, book=self.book1, current_page=1)
        rp.current_page = 7
        rp.save(update_fields=['current_page', 'updated_at'])
        rp.refresh_from_db()
        self.assertEqual(rp.current_page, 7)

    def test_str_is_meaningful(self):
        rp = ReadingProgress.objects.create(user=self.user1, book=self.book1, current_page=3)
        result = str(rp)
        self.assertIn(self.user1.username, result)
        self.assertIn(self.book1.title, result)
        self.assertIn('3', result)


# ---------------------------------------------------------------------------
# Reader Resume Tests
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReaderResumeTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = make_user('resume_user1')
        self.user2 = make_user('resume_user2')
        self.book = make_book('Resume Book')

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_active_subscriber_with_no_progress_gets_initial_page_1(self):
        make_active_subscription(self.user1)
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['initial_page'], 1)

    def test_active_subscriber_with_saved_progress_receives_saved_page(self):
        make_active_subscription(self.user1)
        ReadingProgress.objects.create(user=self.user1, book=self.book, current_page=5)
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['initial_page'], 5)

    def test_one_users_saved_page_is_not_used_for_another_user(self):
        make_active_subscription(self.user1)
        make_active_subscription(self.user2)
        ReadingProgress.objects.create(user=self.user2, book=self.book, current_page=10)
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        # user1 has no progress so they should see page 1, not user2's page 10
        self.assertEqual(response.context['initial_page'], 1)

    def test_reader_still_requires_active_subscription(self):
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)

    def test_expired_subscriber_cannot_use_saved_progress_to_read(self):
        make_expired_subscription(self.user1)
        ReadingProgress.objects.create(user=self.user1, book=self.book, current_page=8)
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)

    def test_future_subscriber_cannot_use_saved_progress_to_read(self):
        make_future_subscription(self.user1)
        ReadingProgress.objects.create(user=self.user1, book=self.book, current_page=3)
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)

    def test_unpublished_book_remains_inaccessible(self):
        make_active_subscription(self.user1)
        self.book.is_published = False
        self.book.save()
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(response.status_code, 404)

    def test_missing_pdf_behavior_remains_correct(self):
        make_active_subscription(self.user1)
        no_pdf_book = make_book(title='No PDF Resume', has_pdf=False)
        self.client.login(username='resume_user1', password='testpass123')
        response = self.client.get(reverse('reading:reader', args=[no_pdf_book.pk]))
        self.assertEqual(response.status_code, 404)

    def test_visiting_reader_does_not_create_progress_record(self):
        """Progress records are only created by the progress_update endpoint, not by visiting reader."""
        make_active_subscription(self.user1)
        self.client.login(username='resume_user1', password='testpass123')
        self.client.get(reverse('reading:reader', args=[self.book.pk]))
        self.assertEqual(ReadingProgress.objects.filter(user=self.user1, book=self.book).count(), 0)


# ---------------------------------------------------------------------------
# Progress Endpoint Tests
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProgressUpdateEndpointTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = make_user('prog_user1')
        self.user2 = make_user('prog_user2')
        self.book = make_book('Progress Book')
        self.progress_url = reverse('reading:progress_update', args=[self.book.pk])

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_anonymous_user_cannot_update_progress(self):
        response = self.client.post(self.progress_url, {'page': 3})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_authenticated_user_without_subscription_cannot_update_progress(self):
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 3})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_expired_subscriber_cannot_update_progress(self):
        make_expired_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 3})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_future_subscriber_cannot_update_progress(self):
        make_future_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 3})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_active_subscriber_can_create_progress(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 4})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['current_page'], 4)
        self.assertEqual(ReadingProgress.objects.count(), 1)
        rp = ReadingProgress.objects.first()
        self.assertEqual(rp.user, self.user1)
        self.assertEqual(rp.current_page, 4)

    def test_progress_update_requires_csrf(self):
        make_active_subscription(self.user1)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user1)
        response = csrf_client.post(self.progress_url, {'page': 4})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ReadingProgress.objects.exists())

    def test_active_subscriber_can_update_existing_progress(self):
        make_active_subscription(self.user1)
        ReadingProgress.objects.create(user=self.user1, book=self.book, current_page=2)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 7})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['current_page'], 7)
        rp = ReadingProgress.objects.get(user=self.user1, book=self.book)
        self.assertEqual(rp.current_page, 7)

    def test_second_update_does_not_create_duplicate_record(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        self.client.post(self.progress_url, {'page': 3})
        self.client.post(self.progress_url, {'page': 5})
        self.assertEqual(ReadingProgress.objects.filter(user=self.user1, book=self.book).count(), 1)

    def test_get_cannot_update_progress(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.get(self.progress_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_page_value_is_required(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])

    def test_non_integer_page_rejected(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 'abc'})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])

    def test_page_0_rejected(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 0})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_negative_page_rejected(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': -5})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_nonexistent_book_returns_404(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(
            reverse('reading:progress_update', args=[99999]),
            {'page': 1}
        )
        self.assertEqual(response.status_code, 404)

    def test_unpublished_book_cannot_receive_progress(self):
        self.book.is_published = False
        self.book.save()
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        response = self.client.post(self.progress_url, {'page': 1})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(ReadingProgress.objects.count(), 0)

    def test_progress_belongs_only_to_request_user(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        self.client.post(self.progress_url, {'page': 3})
        rp = ReadingProgress.objects.first()
        self.assertEqual(rp.user, self.user1)

    def test_forged_user_id_in_post_cannot_change_ownership(self):
        make_active_subscription(self.user1)
        self.client.login(username='prog_user1', password='testpass123')
        # Attempt to forge ownership by sending user2's pk in POST data
        self.client.post(self.progress_url, {'page': 3, 'user': self.user2.pk, 'user_id': self.user2.pk})
        rp = ReadingProgress.objects.first()
        # The record must belong to the logged-in user1, never user2
        self.assertEqual(rp.user, self.user1)
        self.assertNotEqual(rp.user, self.user2)

    def test_one_user_cannot_update_another_users_progress(self):
        make_active_subscription(self.user1)
        make_active_subscription(self.user2)
        # user2 has existing progress at page 9
        ReadingProgress.objects.create(user=self.user2, book=self.book, current_page=9)
        # user1 posts to the same book's progress endpoint
        self.client.login(username='prog_user1', password='testpass123')
        self.client.post(self.progress_url, {'page': 1})
        # user2's record must be unchanged at page 9
        user2_rp = ReadingProgress.objects.get(user=self.user2, book=self.book)
        self.assertEqual(user2_rp.current_page, 9)


# ---------------------------------------------------------------------------
# Template and CSRF Tests for Phase 15
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReaderProgressTemplateTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('tmpl15_user')
        self.book = make_book('Template15 Book')

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def _get_reader(self):
        make_active_subscription(self.user)
        self.client.login(username='tmpl15_user', password='testpass123')
        return self.client.get(reverse('reading:reader', args=[self.book.pk]))

    def test_reader_contains_progress_update_url(self):
        response = self._get_reader()
        expected_url = reverse('reading:progress_update', args=[self.book.pk])
        self.assertContains(response, expected_url)

    def test_reader_contains_csrf_token(self):
        response = self._get_reader()
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_reader_receives_numeric_initial_page(self):
        response = self._get_reader()
        self.assertIn('initial_page', response.context)
        self.assertIsInstance(response.context['initial_page'], int)

    def test_reader_clamps_saved_page_to_pdf_page_range(self):
        response = self._get_reader()
        self.assertContains(
            response,
            'Math.max(1, Math.min(SERVER_INITIAL_PAGE, pdfDoc.numPages))',
        )

    def test_reader_does_not_expose_pdf_file_url(self):
        response = self._get_reader()
        content = response.content.decode()
        self.assertNotIn('books/pdfs/', content)
        self.assertNotIn('/media/', content)

    def test_reader_does_not_expose_receipt_file_url(self):
        response = self._get_reader()
        content = response.content.decode()
        self.assertNotIn('subscriptions/receipts/', content)

    def test_progress_feature_does_not_add_download_button(self):
        response = self._get_reader()
        content = response.content.decode().lower()
        self.assertNotIn('download', content)

    def test_progress_feature_does_not_add_print_button(self):
        response = self._get_reader()
        content = response.content.decode().lower()
        self.assertNotIn('window.print', content)
        self.assertNotIn('type="button"\nwindow', content)


# ---------------------------------------------------------------------------
# My Library Dashboard Tests
# ---------------------------------------------------------------------------

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class MyLibraryDashboardTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_a = make_user('library_user_a')
        self.user_b = make_user('library_user_b')
        self.book_a = make_book('User A Library Book')
        self.book_b = make_book('User B Private Book')
        self.library_url = reverse('reading:my_library')

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def login_user_a(self):
        self.client.login(username='library_user_a', password='testpass123')

    def test_library_url_resolves_to_named_route(self):
        match = resolve('/reading/library/')
        self.assertEqual(match.namespace, 'reading')
        self.assertEqual(match.url_name, 'my_library')

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.library_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_authenticated_user_gets_200(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertEqual(response.status_code, 200)

    def test_user_without_subscription_can_view_dashboard(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'لا يوجد اشتراك نشط حالياً')

    def test_expired_subscriber_can_view_dashboard(self):
        make_expired_subscription(self.user_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertTemplateUsed(response, 'reading/my_library.html')

    def test_dashboard_contains_arabic_heading(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, 'مكتبتي')

    def test_current_users_progress_is_shown(self):
        ReadingProgress.objects.create(
            user=self.user_a,
            book=self.book_a,
            current_page=12,
        )
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.book_a.title)

    def test_another_users_progress_is_hidden(self):
        ReadingProgress.objects.create(
            user=self.user_b,
            book=self.book_b,
            current_page=42,
        )
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertNotContains(response, self.book_b.title)
        self.assertNotContains(response, 'الصفحة الأخيرة: 42')

    def test_saved_current_page_is_shown(self):
        ReadingProgress.objects.create(
            user=self.user_a,
            book=self.book_a,
            current_page=12,
        )
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, 'الصفحة الأخيرة: 12')

    def test_progress_book_title_is_shown(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.book_a.title)

    def test_progress_author_is_shown(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.book_a.author.name)

    def test_progress_category_is_shown(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.book_a.category.name)

    def test_continue_reading_link_uses_protected_reader(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        reader_url = reverse('reading:reader', args=[self.book_a.pk])
        self.assertContains(response, reader_url)

    def test_dashboard_does_not_link_to_pdf_file_endpoint(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        pdf_url = reverse('reading:pdf_file', args=[self.book_a.pk])
        self.assertNotContains(response, pdf_url)

    def test_unpublished_book_progress_is_hidden(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.book_a.is_published = False
        self.book_a.save(update_fields=['is_published'])
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertNotContains(response, self.book_a.title)

    def test_empty_progress_section_shows_arabic_state(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, 'لا توجد كتب قيد القراءة حالياً.')

    def test_current_users_favorite_is_shown(self):
        Favorite.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.book_a.title)

    def test_another_users_favorite_is_hidden(self):
        Favorite.objects.create(user=self.user_b, book=self.book_b)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertNotContains(response, self.book_b.title)

    def test_favorite_title_author_and_category_are_shown(self):
        Favorite.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.book_a.title)
        self.assertContains(response, self.book_a.author.name)
        self.assertContains(response, self.book_a.category.name)

    def test_favorite_links_to_book_detail(self):
        Favorite.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        detail_url = reverse('catalog:book_detail', args=[self.book_a.pk])
        self.assertContains(response, detail_url)

    def test_unpublished_favorite_is_hidden(self):
        Favorite.objects.create(user=self.user_a, book=self.book_a)
        self.book_a.is_published = False
        self.book_a.save(update_fields=['is_published'])
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertNotContains(response, self.book_a.title)

    def test_empty_favorites_section_shows_arabic_state(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, 'لا توجد كتب في المفضلة حالياً.')

    def test_dashboard_isolates_favorites_and_progress_by_user(self):
        Favorite.objects.create(user=self.user_a, book=self.book_a)
        Favorite.objects.create(user=self.user_b, book=self.book_b)
        ReadingProgress.objects.create(
            user=self.user_a,
            book=self.book_a,
            current_page=7,
        )
        ReadingProgress.objects.create(
            user=self.user_b,
            book=self.book_b,
            current_page=42,
        )

        self.login_user_a()
        response = self.client.get(self.library_url)

        self.assertContains(response, self.book_a.title)
        self.assertContains(response, 'الصفحة الأخيرة: 7')
        self.assertNotContains(response, self.book_b.title)
        self.assertNotContains(response, 'الصفحة الأخيرة: 42')

    def test_user_id_query_parameter_cannot_change_ownership(self):
        Favorite.objects.create(user=self.user_b, book=self.book_b)
        ReadingProgress.objects.create(
            user=self.user_b,
            book=self.book_b,
            current_page=42,
        )
        self.login_user_a()
        response = self.client.get(
            self.library_url,
            {'user_id': self.user_b.pk, 'user': self.user_b.pk},
        )
        self.assertNotContains(response, self.book_b.title)
        self.assertNotContains(response, 'الصفحة الأخيرة: 42')

    def test_active_subscription_status_is_shown(self):
        make_active_subscription(self.user_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, 'اشتراكك نشط')

    def test_expired_subscription_is_not_shown_as_active(self):
        make_expired_subscription(self.user_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, 'لا يوجد اشتراك نشط حالياً')

    def test_authenticated_navigation_contains_my_library_link(self):
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertContains(response, self.library_url)
        self.assertContains(response, 'مكتبتي')

    def test_dashboard_exposes_no_raw_pdf_or_receipt_paths(self):
        Favorite.objects.create(user=self.user_a, book=self.book_a)
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        content = response.content.decode()
        self.assertNotIn('books/pdfs/', content)
        self.assertNotIn('subscriptions/receipts/', content)
        self.assertNotIn('/media/', content)

    def test_dashboard_has_no_pdf_download_button(self):
        ReadingProgress.objects.create(user=self.user_a, book=self.book_a)
        self.login_user_a()
        response = self.client.get(self.library_url)
        self.assertNotIn('download', response.content.decode().lower())
