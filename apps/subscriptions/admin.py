from django.contrib import admin
from .models import SubscriptionRequest, Subscription


@admin.register(SubscriptionRequest)
class SubscriptionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'payment_method')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'start_at', 'end_at', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
