from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionRequest, Subscription


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
        from django.db import IntegrityError
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
        # start in the past, end in the future
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
