from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionRequest, Subscription


REQUEST_LIST_URL = '/subscriptions/'
REQUEST_CREATE_URL = '/subscriptions/request/'

VALID_POST = {
    'payment_method': 'bank_transfer',
    'receipt_file': '',
}


def make_user(username='testuser', password='testpass123'):
    return User.objects.create_user(username=username, password=password)


def make_pending_request(user):
    return SubscriptionRequest.objects.create(
        user=user,
        payment_method='bank_transfer',
        receipt_file='subscriptions/receipts/test.pdf',
        status=SubscriptionRequest.Status.PENDING,
    )


# ---------------------------------------------------------------------------
# Phase 10 regression tests (model tests) kept intact above this file's scope
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
        result = str(sub)
        self.assertIn('subuser', result)

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
        fake_file = io.BytesIO(b'fake receipt content')
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
        fake_file = io.BytesIO(b'fake receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {
            'payment_method': 'cash',
            'receipt_file': fake_file,
        })
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertEqual(req.user, self.user)

    def test_new_request_status_defaults_to_pending(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': fake_file,
        })
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertEqual(req.status, SubscriptionRequest.Status.PENDING)

    def test_user_cannot_forge_approved_status_via_post(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': fake_file,
            'status': 'APPROVED',
        })
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertEqual(req.status, SubscriptionRequest.Status.PENDING)

    def test_user_cannot_forge_reviewed_by_via_post(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': fake_file,
            'reviewed_by': self.other_user.pk,
        })
        req = SubscriptionRequest.objects.get(user=self.user)
        self.assertIsNone(req.reviewed_by)

    def test_user_cannot_set_another_user_via_post(self):
        self.client.login(username='viewuser', password='testpass123')
        import io
        fake_file = io.BytesIO(b'receipt')
        fake_file.name = 'r.pdf'
        self.client.post(self.create_url, {
            'payment_method': 'bank_transfer',
            'receipt_file': fake_file,
            'user': self.other_user.pk,
        })
        for req in SubscriptionRequest.objects.all():
            self.assertEqual(req.user, self.user)

    def test_invalid_form_does_not_create_request(self):
        self.client.login(username='viewuser', password='testpass123')
        self.client.post(self.create_url, {
            'payment_method': '',
            'receipt_file': '',
        })
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
        # other user's requests shouldn't appear
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
        from apps.subscriptions.models import SubscriptionRequest
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
        # Try to approve again (should be skipped, already APPROVED)
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
        # Try to reject already-approved
        self._run_action('reject', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.APPROVED)
        self.assertEqual(req.reviewed_at, original_reviewed_at)

    def test_already_rejected_request_is_not_reprocessed(self):
        req = self._pending_request()
        self._run_action('reject', [req.pk])
        req.refresh_from_db()
        original_reviewed_at = req.reviewed_at
        # Try to approve already-rejected
        self._run_action('approve', [req.pk])
        req.refresh_from_db()
        self.assertEqual(req.status, SubscriptionRequest.Status.REJECTED)
        self.assertEqual(req.reviewed_at, original_reviewed_at)
