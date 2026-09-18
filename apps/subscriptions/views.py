from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from .forms import SubscriptionRequestForm
from .models import SubscriptionRequest
from .services import get_active_subscription


@login_required
def request_create(request):
    if request.method == 'POST':
        form = SubscriptionRequestForm(request.POST, request.FILES)
        if form.is_valid():
            sub_request = form.save(commit=False)
            sub_request.user = request.user
            sub_request.status = SubscriptionRequest.Status.PENDING
            sub_request.save()
            messages.success(request, 'تم إرسال طلب الاشتراك بنجاح. سيتم مراجعته من قبل الإدارة.')
            return redirect('subscriptions:request_list')
    else:
        form = SubscriptionRequestForm()
    return render(request, 'subscriptions/request_form.html', {'form': form})


@login_required
def request_list(request):
    requests = SubscriptionRequest.objects.filter(user=request.user).order_by('-created_at')
    active_subscription = get_active_subscription(request.user)
    return render(request, 'subscriptions/request_list.html', {
        'requests': requests,
        'active_subscription': active_subscription,
    })


@staff_member_required(login_url='admin:login')
def protected_receipt_file(request, path):
    """
    Serve receipt file only to staff members.
    Anonymous users are redirected to the admin login page.
    Non-staff users are denied access.
    """
    sub_request = SubscriptionRequest.objects.filter(receipt_file='subscriptions/receipts/' + path).first()
    if not sub_request or not sub_request.receipt_file:
        raise Http404("إيصال الدفع غير موجود.")
    
    try:
        file = sub_request.receipt_file.open('rb')
    except (FileNotFoundError, OSError):
        raise Http404("ملف الإيصال غير موجود على الخادم.")
    
    response = FileResponse(file, content_type='application/pdf')
    # Using attachment rather than inline for safety against uploaded content
    response['Content-Disposition'] = f'attachment; filename="receipt-{sub_request.pk}.pdf"'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    return response
