from django.db import models
from django.conf import settings
from django.utils import timezone


class SubscriptionRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'قيد الانتظار'
        APPROVED = 'APPROVED', 'مقبول'
        REJECTED = 'REJECTED', 'مرفوض'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription_requests',
    )
    payment_method = models.CharField(max_length=50)
    receipt_file = models.FileField(upload_to='subscriptions/receipts/')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_subscription_requests',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SubscriptionRequest({self.user}, {self.status})"


class Subscription(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    request = models.OneToOneField(
        SubscriptionRequest,
        on_delete=models.PROTECT,
        related_name='subscription',
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Subscription({self.user}, {self.start_at.date()} -> {self.end_at.date()})"

    def is_active(self):
        now = timezone.now()
        return self.start_at <= now <= self.end_at
