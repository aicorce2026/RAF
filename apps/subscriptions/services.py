from django.utils import timezone
from .models import Subscription


def has_active_subscription(user):
    """
    Return True if the given user currently has an active subscription.

    A subscription is active when:
        start_at <= timezone.now() < end_at

    Anonymous users always return False.
    Authenticated users with no subscription return False.
    If the user has multiple subscriptions, any active one is sufficient.
    """
    if not user or not user.is_authenticated:
        return False
    now = timezone.now()
    return Subscription.objects.filter(
        user=user,
        start_at__lte=now,
        end_at__gt=now,
    ).exists()


def get_active_subscription(user):
    """
    Return the first active Subscription for the user, or None.
    """
    if not user or not user.is_authenticated:
        return None
    now = timezone.now()
    return Subscription.objects.filter(
        user=user,
        start_at__lte=now,
        end_at__gt=now,
    ).first()
