from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SubscriptionRequestForm
from .models import SubscriptionRequest


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
    return render(request, 'subscriptions/request_list.html', {'requests': requests})
