from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from apps.core.validators import RECEIPT_MAX_SIZE
from .models import SubscriptionRequest, Subscription
from .services import has_active_subscription, get_active_subscription
from .decorators import active_subscription_required


REQUEST_LIST_URL = '/subscriptions/'
REQUEST_CREATE_URL = '/subscriptions/request/'


def make_user(username='testuser', password='testpass123'):
    return User.objects.create_user(username=username, password=password)


def make_pending_request(user):
    return SubscriptionRequest.objects.create(
        user=user,
        payment_method='bank_transfer',
        receipt_file='subscriptions/receipts/test.pdf',
        status=SubscriptionRequest.Status.PENDING,
    )


def make_approved_request(user):
    return SubscriptionRequest.objects.create(
        user=user,
        payment_method='bank_transfer',
        receipt_file='subscriptions/receipts/test.pdf',
        status=SubscriptionRequest.Status.APPROVED,
    )


def make_active_subscription(user):
    req = make_approved_request(user)
    now = timezone.now()
    return Subscription.objects.create(
        user=user,
        request=req,
        start_at=now - timedelta(days=1),
        end_at=now + timedelta(days=29),
    )


# ---------------------------------------------------------------------------
# Phase 10 regression: SubscriptionRequest model tests
# ---------------------------------------------------------------------------

class SubscriptionRequestModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='subscriber', password='testpass123')
        self.reviewer = User.objects.create_user(username='reviewer', password='testpass123')

    def _make_request(self, **kwargs):
        defaults = {
            'user': self.user,
            'payment_method': 'Bank Transfer',
            'receipt_file': 'subscriptions/receipts/test.pdf',
        }
        defaults.update(kwargs)
        return SubscriptionRequest.objects.create(**defaults)

    def test_request_creation(self):
        req = self._make_request()
        self.assertIsNotNone(req.pk)

    def test_default_status_is_pending(self):
        req = self._make_request()
        self.assertEqual(req.status, SubscriptionRequest.Status.PENDING)

    def test_user_relationship_works(self):
        req = self._make_request()
        self.assertEqual(req.user, self.user)
        self.assertIn(req, self.user.subscription_requests.all())

    def test_receipt_path_uses_correct_prefix(self):
        req = self._make_request(receipt_file='subscriptions/receipts/receipt123.pdf')
        self.assertTrue(req.receipt_file.name.startswith('subscriptions/receipts/'))

    def test_str_representation(self):
        req = self._make_request()
        self.assertIn('subscriber', str(req))
        self.assertIn('PENDING', str(req))

    def test_approved_status_can_be_stored(self):
        req = self._make_request(status=SubscriptionRequest.Status.APPROVED)
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.APPROVED)

    def test_rejected_status_can_be_stored(self):
        req = self._make_request(status=SubscriptionRequest.Status.REJECTED)
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.REJECTED)

    def test_admin_note_is_optional(self):
        req = self._make_request()
        self.assertEqual(req.admin_note, '')

    def test_admin_note_can_be_set(self):
        req = self._make_request(admin_note='Receipt verified by admin.')
        self.assertEqual(req.admin_note, 'Receipt verified by admin.')

    def test_reviewed_by_can_be_null(self):
        req = self._make_request()
        self.assertIsNone(req.reviewed_by)

    def test_reviewed_at_can_be_null(self):
        req = self._make_request()
        self.assertIsNone(req.reviewed_at)


class SubscriptionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='subuser', password='testpass123')
        self.sub_request = SubscriptionRequest.objects.create(
            user=self.user,
            payment_method='Bank Transfer',
            receipt_file='subscriptions/receipts/test.pdf',
            status=SubscriptionRequest.Status.APPROVED,
        )
        self.now = timezone.now()

    def _make_subscription(self, start_offset=0, end_offset=30):
        return Subscription.objects.create(
            user=self.user,
            request=self.sub_request,
            start_at=self.now + timedelta(days=start_offset),
            end_at=self.now + timedelta(days=end_offset),
        )

    def test_subscription_creation(self):
        sub = self._make_subscription()
        self.assertIsNotNone(sub.pk)

    def test_user_relationship_works(self):
        sub = self._make_subscription()
        self.assertEqual(sub.user, self.user)
        self.assertIn(sub, self.user.subscriptions.all())

    def test_request_relationship_works(self):
        sub = self._make_subscription()
        self.assertEqual(sub.request, self.sub_request)

    def test_one_request_cannot_have_two_subscriptions(self):
        self._make_subscription()
        with self.assertRaises(Exception):
            Subscription.objects.create(
                user=self.user,
                request=self.sub_request,
                start_at=self.now,
                end_at=self.now + timedelta(days=30),
            )

    def test_str_representation(self):
        sub = self._make_subscription()
        self.assertIn('subuser', str(sub))

    def test_active_subscription_is_active(self):
        sub = Subscription.objects.create(
            user=self.user,
            request=self.sub_request,
            start_at=self.now - timedelta(days=1),
            end_at=self.now + timedelta(days=29),
        )
        self.assertTrue(sub.is_active())

    def test_expired_subscription_is_not_active(self):
        sub = Subscription.objects.create(
            user=self.user,
            request=self.sub_request,
            start_at=self.now - timedelta(days=60),
            end_at=self.now - timedelta(days=30),
        )
        self.assertFalse(sub.is_active())

    def test_future_subscription_is_not_active(self):
        sub = Subscription.objects.create(
            user=self.user,
            request=self.sub_request,
            start_at=self.now + timedelta(days=5),
            end_at=self.now + timedelta(days=35),
        )
        self.assertFalse(sub.is_active())

    def test_subscription_is_inactive_at_exact_end_time(self):
        sub = self._make_subscription(start_offset=-1, end_offset=0)
        with patch('apps.subscriptions.models.timezone.now', return_value=sub.end_at):
            self.assertFalse(sub.is_active())


# ---------------------------------------------------------------------------
# Phase 11: User workflow tests
# ---------------------------------------------------------------------------

class SubscriptionRequestViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('viewuser')
        self.other_user = make_user('otheruser')
        self.create_url = reverse('subscriptions:request_create')
        self.list_url = reverse('subscriptions:request_list')

    def test_anonymous_cannot_access_request_form(self):
        response = self.client.get(self.create_url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next={self.create_url}')

    def test_authenticated_user_can_access_request_form(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/request_form.html')

    def test_request_form_uses_multipart_encoding(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertContains(response, 'multipart/form-data')

    def test_authenticated_user_can_submit_valid_request(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'%PDF-1.4 fake receipt content')
        fake_file.name = 'receipt.pdf'
        response = self.client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': fake_file,
        })
        self.assertEqual(SubscriptionRequest.objects.filter(user=self.user).count(), 1)
        self.assertRedirects(response, self.list_url)

    def test_created_request_belongs_to_logged_in_user(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'%PDF-1.4 fake receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {'payment_method': 'cash', 'receipt_file': fake_file})
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertEqual(req.user, self.user)

    def test_new_request_status_defaults_to_pending(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'%PDF-1.4 receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {'payment_method': 'bank_transfer', 'receipt_file': fake_file})
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertEqual(req.status, SubscriptionRequest.Status.PENDING)

    def test_user_cannot_forge_approved_status_via_post(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'%PDF-1.4 receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {'payment_method': 'bank_transfer', 'receipt_file': fake_file, 'status': 'APPROVED'})
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertEqual(req.status, SubscriptionRequest.Status.PENDING)

    def test_user_cannot_forge_reviewed_by_via_post(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'%PDF-1.4 receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {'payment_method': 'bank_transfer', 'receipt_file': fake_file, 'reviewed_by': self.other_user.pk})
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertIsNone(req.reviewed_by)

    def test_user_cannot_set_another_user_via_post(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'%PDF-1.4 receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {'payment_method': 'bank_transfer', 'receipt_file': fake_file, 'user': self.other_user.pk})
        for req in SubscriptionRequest.objects.all():
            self.assertEqual(req.user, self.user)

    def test_invalid_form_does_not_create_request(self):
        self.client.login(username='viewuser', password='testpass123')
        self.client.post(self.create_url, {'payment_method': '', 'receipt_file': ''})
        self.assertEqual(SubscriptionRequest.objects.filter(user=self.user).count(), 0)

    def test_anonymous_cannot_access_request_list(self):
        response = self.client.get(self.list_url)
        self.assertNotEqual(response.status_code, 200)

    def test_request_list_returns_200_for_authenticated(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/request_list.html')

    def test_request_list_shows_own_requests(self):
        make_pending_request(self.user)
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'bank_transfer')

    def test_request_list_does_not_expose_other_users_requests(self):
        make_pending_request(self.other_user)
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertEqual(SubscriptionRequest.objects.filter(user=self.user).count(), 0)

    def test_receipt_url_not_in_request_list(self):
        make_pending_request(self.user)
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertNotContains(response, 'subscriptions/receipts')
        self.assertNotContains(response, '/media/')

    def test_empty_request_list_has_arabic_empty_state(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'لا توجد طلبات اشتراك')


    def _post_receipt(self, filename, content, payment_method='bank_transfer'):
        self.client.login(username='viewuser', password='testpass123')
        upload = SimpleUploadedFile(filename, content)
        return self.client.post(self.create_url, {
            'payment_method': payment_method,
            'receipt_file': upload,
        })

    def test_invalid_payment_method_is_rejected(self):
        response = self._post_receipt('receipt.pdf', b'%PDF-1.4 receipt', 'crypto')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscriptionRequest.objects.exists())

    def test_invalid_receipt_extension_is_rejected(self):
        response = self._post_receipt('receipt.exe', b'%PDF-1.4 receipt')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscriptionRequest.objects.exists())

    def test_receipt_content_must_match_extension(self):
        response = self._post_receipt('receipt.pdf', b'not a real PDF')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscriptionRequest.objects.exists())

    def test_zero_byte_receipt_is_rejected(self):
        response = self._post_receipt('receipt.png', b'')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscriptionRequest.objects.exists())

    def test_oversized_receipt_is_rejected(self):
        self.client.login(username='viewuser', password='testpass123')
        upload = SimpleUploadedFile(
            'receipt.pdf',
            b'%PDF-' + (b'x' * RECEIPT_MAX_SIZE),
        )
        response = self.client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': upload,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscriptionRequest.objects.exists())

    def test_valid_jpeg_receipt_is_accepted(self):
        response = self._post_receipt('receipt.jpg', b'\xff\xd8\xff receipt')
        self.assertRedirects(response, self.list_url)
        self.assertEqual(SubscriptionRequest.objects.count(), 1)

    def test_receipt_validation_runs_on_model_full_clean(self):
        sub_request = SubscriptionRequest(
            user=self.user,
            payment_method='bank_transfer',
            receipt_file=SimpleUploadedFile('receipt.pdf', b'not a PDF'),
        )
        with self.assertRaises(ValidationError):
            sub_request.full_clean()

    def test_get_request_form_does_not_create_request(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscriptionRequest.objects.exists())

    def test_request_creation_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        response = csrf_client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': SimpleUploadedFile(
                'receipt.pdf', b'%PDF-1.4 receipt'
            ),
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SubscriptionRequest.objects.exists())


# ---------------------------------------------------------------------------
# Phase 11: Admin workflow tests
# ---------------------------------------------------------------------------

class SubscriptionAdminWorkflowTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin11', password='adminpass123', email='admin@test.com'
        )
        self.regular_user = make_user('reguser')
        self.client = Client()
        self.client.login(username='admin11', password='adminpass123')

    def _pending_request(self):
        return make_pending_request(self.regular_user)

    def _run_action(self, action_name, queryset_pks):
        from django.contrib.admin.sites import site
        admin_instance = site._registry[SubscriptionRequest]
        request_obj = self.client.get('/admin/').wsgi_request
        request_obj.user = self.admin_user
        qs = SubscriptionRequest.objects.filter(pk__in=queryset_pks)
        if action_name == 'approve':
            from apps.subscriptions.admin import approve_requests
            approve_requests(admin_instance, request_obj, qs)
        else:
            from apps.subscriptions.admin import reject_requests
            reject_requests(admin_instance, request_obj, qs)

    def test_approval_changes_pending_to_approved(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.APPROVED)

    def test_approval_records_reviewed_by(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.reviewed_by, self.admin_user)

    def test_approval_records_reviewed_at(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        req.refresh_from_db()
        self.assertIsNotNone(req.reviewed_at)

    def test_approval_creates_exactly_one_subscription(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        self.assertEqual(Subscription.objects.filter(request=req).count(), 1)

    def test_approved_subscription_lasts_30_days(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        sub = Subscription.objects.get(request=req)
        duration = sub.end_at - sub.start_at
        self.assertAlmostEqual(duration.total_seconds(), 30 * 24 * 3600, delta=5)

    def test_repeated_approval_does_not_create_duplicate_subscription(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        self._run_action('approve', [req.pk])
        self.assertEqual(Subscription.objects.filter(request=req).count(), 1)

    def test_rejection_changes_pending_to_rejected(self):
        req = self._pending_request()
        self._run_action('reject', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.REJECTED)

    def test_rejection_records_reviewer_and_time(self):
        req = self._pending_request()
        self._run_action('reject', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.reviewed_by, self.admin_user)
        self.assertIsNotNone(req.reviewed_at)

    def test_rejection_creates_no_subscription(self):
        req = self._pending_request()
        self._run_action('reject', [req.pk])
        self.assertEqual(Subscription.objects.filter(request=req).count(), 0)

    def test_already_approved_request_is_not_reprocessed(self):
        req = self._pending_request()
        self._run_action('approve', [req.pk])
        req.refresh_from_db()
        original_reviewed_at = req.reviewed_at
        self._run_action('reject', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.APPROVED)
        self.assertEqual(req.reviewed_at, original_reviewed_at)

    def test_already_rejected_request_is_not_reprocessed(self):
        req = self._pending_request()
        self._run_action('reject', [req.pk])
        req.refresh_from_db()
        original_reviewed_at = req.reviewed_at
        self._run_action('approve', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.REJECTED)
        self.assertEqual(req.reviewed_at, original_reviewed_at)


    def test_approval_database_error_is_not_silently_swallowed(self):
        req = self._pending_request()
        with patch(
            'apps.subscriptions.admin.Subscription.objects.create',
            side_effect=DatabaseError('simulated database failure'),
        ):
            with self.assertRaises(DatabaseError):
                self._run_action('approve', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.PENDING)
        self.assertIsNone(req.reviewed_by)


# ---------------------------------------------------------------------------
# Phase 12: has_active_subscription service tests
# ---------------------------------------------------------------------------

class HasActiveSubscriptionServiceTests(TestCase):

    def setUp(self):
        self.user = make_user('svcuser')
        self.now = timezone.now()

    def test_anonymous_user_returns_false(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(has_active_subscription(AnonymousUser()))

    def test_none_returns_false(self):
        self.assertFalse(has_active_subscription(None))

    def test_authenticated_user_with_no_subscription_returns_false(self):
        self.assertFalse(has_active_subscription(self.user))

    def test_active_subscription_returns_true(self):
        make_active_subscription(self.user)
        self.assertTrue(has_active_subscription(self.user))

    def test_expired_subscription_returns_false(self):
        req = make_approved_request(self.user)
        Subscription.objects.create(
            user=self.user,
            request=req,
            start_at=self.now - timedelta(days=60),
            end_at=self.now - timedelta(days=30),
        )
        self.assertFalse(has_active_subscription(self.user))

    def test_future_subscription_returns_false(self):
        req = make_approved_request(self.user)
        Subscription.objects.create(
            user=self.user,
            request=req,
            start_at=self.now + timedelta(days=5),
            end_at=self.now + timedelta(days=35),
        )
        self.assertFalse(has_active_subscription(self.user))

    def test_multiple_subscriptions_any_active_returns_true(self):
        # One expired, one active
        user2 = make_user('svcuser2')
        req1 = make_approved_request(user2)
        Subscription.objects.create(
            user=user2,
            request=req1,
            start_at=self.now - timedelta(days=60),
            end_at=self.now - timedelta(days=30),
        )
        req2 = SubscriptionRequest.objects.create(
            user=user2,
            payment_method='cash',
            receipt_file='subscriptions/receipts/r2.pdf',
            status=SubscriptionRequest.Status.APPROVED,
        )
        Subscription.objects.create(
            user=user2,
            request=req2,
            start_at=self.now - timedelta(days=1),
            end_at=self.now + timedelta(days=29),
        )
        self.assertTrue(has_active_subscription(user2))


# ---------------------------------------------------------------------------
# Phase 12: active_subscription_required decorator tests
# ---------------------------------------------------------------------------

from django.http import HttpResponse
from django.test import RequestFactory

# Create a minimal protected view for decorator testing
@active_subscription_required
def _protected_view(request):
    return HttpResponse('OK', status=200)


class ActiveSubscriptionDecoratorTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = make_user('decuser')
        self.now = timezone.now()

    def _get_request(self, user=None, path='/protected/'):
        request = self.factory.get(path)
        if user is None:
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        else:
            request.user = user
        return request

    def test_anonymous_user_redirected_to_login(self):
        request = self._get_request(user=None)
        response = _protected_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_authenticated_user_without_subscription_redirected(self):
        request = self._get_request(user=self.user)
        response = _protected_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/subscriptions/', response['Location'])

    def test_expired_subscription_is_denied(self):
        req = make_approved_request(self.user)
        Subscription.objects.create(
            user=self.user,
            request=req,
            start_at=self.now - timedelta(days=60),
            end_at=self.now - timedelta(days=30),
        )
        request = self._get_request(user=self.user)
        response = _protected_view(request)
        self.assertEqual(response.status_code, 302)

    def test_future_subscription_is_denied(self):
        req = make_approved_request(self.user)
        Subscription.objects.create(
            user=self.user,
            request=req,
            start_at=self.now + timedelta(days=5),
            end_at=self.now + timedelta(days=35),
        )
        request = self._get_request(user=self.user)
        response = _protected_view(request)
        self.assertEqual(response.status_code, 302)

    def test_active_subscription_allows_access(self):
        make_active_subscription(self.user)
        request = self._get_request(user=self.user)
        response = _protected_view(request)
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# Phase 12: Subscription status UI tests
# ---------------------------------------------------------------------------

class SubscriptionStatusUITests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user('statususer')
        self.other_user = make_user('otherstatususer')
        self.list_url = reverse('subscriptions:request_list')

    def test_authenticated_user_can_view_subscription_status(self):
        self.client.login(username='statususer', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'حالة الاشتراك')

    def test_active_subscription_dates_are_shown(self):
        sub = make_active_subscription(self.user)
        self.client.login(username='statususer', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'اشتراك نشط')
        self.assertContains(response, sub.start_at.strftime('%Y-%m-%d'))
        self.assertContains(response, sub.end_at.strftime('%Y-%m-%d'))

    def test_no_active_subscription_shows_correct_state(self):
        self.client.login(username='statususer', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'لا يوجد اشتراك نشط')

    def test_another_users_subscription_data_not_exposed(self):
        make_active_subscription(self.other_user)
        self.client.login(username='statususer', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'لا يوجد اشتراك نشط')

    def test_receipt_url_not_exposed_in_status_page(self):
        make_active_subscription(self.user)
        self.client.login(username='statususer', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertNotContains(response, 'subscriptions/receipts')
        self.assertNotContains(response, '/media/')


# ---------------------------------------------------------------------------
# Phase 12: Regression — public catalog pages remain public
# ---------------------------------------------------------------------------

class PublicCatalogRegressionTests(TestCase):

    def setUp(self):
        self.client = Client()
        from apps.catalog.models import Author, Category, Book
        self.author = Author.objects.create(name='Pub Author')
        self.category = Category.objects.create(name='Pub Category')
        self.book = Book.objects.create(
            title='Public Book',
            author=self.author,
            category=self.category,
            is_published=True,
            pdf_file='books/pdfs/pub.pdf',
        )

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
# Phase 13 Security Correction: Protected Receipt Endpoint Tests
# ---------------------------------------------------------------------------

import tempfile
import os
from django.test import override_settings

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProtectedReceiptEndpointTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_superuser('staffuser', 'staff@test.com', 'testpass123')
        self.normal_user = make_user('normaluser', 'testpass123')
        
        # Create a pending request with an actual file
        self.sub_request = SubscriptionRequest.objects.create(
            user=self.normal_user,
            payment_method='bank_transfer',
            status=SubscriptionRequest.Status.PENDING,
        )
        self.sub_request.receipt_file = SimpleUploadedFile(
            'test_receipt.pdf', b'%PDF-1.4 fake receipt', content_type='application/pdf'
        )
        self.sub_request.save()
        
        # The URL that would normally be served by Django dev server
        # The re_path uses (?P<path>.+) which captures everything after media/subscriptions/receipts/
        # e.g., filename
        filename = os.path.basename(self.sub_request.receipt_file.name)
        self.receipt_url = f'/media/subscriptions/receipts/{filename}'

    def tearDown(self):
        import shutil
        from django.conf import settings
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_anonymous_cannot_fetch_receipt(self):
        response = self.client.get(self.receipt_url)
        # Should redirect to admin login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_authenticated_normal_user_cannot_fetch_receipt(self):
        self.client.login(username='normaluser', password='testpass123')
        response = self.client.get(self.receipt_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])
        
    def test_another_normal_user_cannot_fetch_receipt(self):
        another_user = make_user('anotheruser', 'testpass123')
        self.client.login(username='anotheruser', password='testpass123')
        response = self.client.get(self.receipt_url)
        self.assertEqual(response.status_code, 302)
        
    def test_staff_user_can_fetch_receipt(self):
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(self.receipt_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_missing_receipt_returns_404_for_staff(self):
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get('/media/subscriptions/receipts/nonexistent.pdf')
        self.assertEqual(response.status_code, 404)

    def test_receipt_path_traversal_returns_404(self):
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(
            '/media/subscriptions/receipts/%2e%2e%2fsettings.py'
        )
        self.assertEqual(response.status_code, 404)

    def test_nested_receipt_path_returns_404(self):
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(
            '/media/subscriptions/receipts/nested/test_receipt.pdf'
        )
        self.assertEqual(response.status_code, 404)
        
    def test_receipt_response_headers_are_safe(self):
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(self.receipt_url)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('no-store', response['Cache-Control'])
        
    def test_receipt_response_is_attachment_not_inline(self):
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(self.receipt_url)
        disposition = response.get('Content-Disposition', '')
        self.assertIn('attachment', disposition)
        self.assertNotIn('inline', disposition)

    def test_direct_book_pdf_path_remains_blocked(self):
        response = self.client.get('/media/books/pdfs/somebook.pdf')
        self.assertEqual(response.status_code, 403)
