from django import forms
from .models import SubscriptionRequest

PAYMENT_METHOD_CHOICES = [
    ('', '-- اختر طريقة الدفع --'),
    ('bank_transfer', 'تحويل بنكي'),
    ('cash', 'دفع نقدي'),
    ('other', 'أخرى'),
]


class SubscriptionRequestForm(forms.ModelForm):

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        label='طريقة الدفع',
    )

    class Meta:
        model = SubscriptionRequest
        fields = ['payment_method', 'receipt_file']
        labels = {
            'receipt_file': 'إيصال الدفع',
        }
