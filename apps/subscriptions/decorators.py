from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .services import has_active_subscription


def active_subscription_required(view_func):
    """
    Decorator that restricts access to views requiring an active subscription.

    - Anonymous users     → redirect to login page
    - No active subscription → redirect to subscriptions:request_list
    - Active subscription      → view proceeds normally

    Usage:
        @active_subscription_required
        def my_protected_view(request):
            ...
    """
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not has_active_subscription(request.user):
            return redirect('subscriptions:request_list')
        return view_func(request, *args, **kwargs)
    return _wrapped
