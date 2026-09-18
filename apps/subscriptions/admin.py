from django.contrib import admin, messages
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from .models import SubscriptionRequest, Subscription


def approve_requests(modeladmin, request, queryset):
    """Approve selected PENDING subscription requests and create 30-day subscriptions."""
    approved_count = 0
    skipped_count = 0
    for sub_request in queryset:
        if sub_request.status != SubscriptionRequest.Status.PENDING:
            skipped_count += 1
            continue
        with transaction.atomic():
            now = timezone.now()
            sub_request.status = SubscriptionRequest.Status.APPROVED
            sub_request.reviewed_by = request.user
            sub_request.reviewed_at = now
            sub_request.save()
            # Guard against duplicate subscriptions (idempotent).
            if not hasattr(sub_request, 'subscription'):
                Subscription.objects.create(
                    user=sub_request.user,
                    request=sub_request,
                    start_at=now,
                    end_at=now + timedelta(days=30),
                )
        approved_count += 1

    if approved_count:
        messages.success(request, f'تم قبول {approved_count} طلب/طلبات بنجاح وإنشاء الاشتراك.')
    if skipped_count:
        messages.warning(request, f'تم تجاوز {skipped_count} طلب/طلبات (غير معلقة أو مكررة).')


approve_requests.short_description = 'قبول الطلبات المحددة وإنشاء الاشتراك (30 يومًا)'


def reject_requests(modeladmin, request, queryset):
    """Reject selected PENDING subscription requests."""
    rejected_count = 0
    skipped_count = 0
    for sub_request in queryset:
        if sub_request.status != SubscriptionRequest.Status.PENDING:
            skipped_count += 1
            continue
        now = timezone.now()
        sub_request.status = SubscriptionRequest.Status.REJECTED
        sub_request.reviewed_by = request.user
        sub_request.reviewed_at = now
        sub_request.save()
        rejected_count += 1

    if rejected_count:
        messages.success(request, f'تم رفض {rejected_count} طلب/طلبات.')
    if skipped_count:
        messages.warning(request, f'تم تجاوز {skipped_count} طلب/طلبات (غير معلقة).')


reject_requests.short_description = 'رفض الطلبات المحددة'


@admin.register(SubscriptionRequest)
class SubscriptionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'payment_method')
    readonly_fields = ('created_at', 'updated_at')
    actions = [approve_requests, reject_requests]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'start_at', 'end_at', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
