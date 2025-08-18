# shop/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(choices=Order.PAYMENT_METHODS),
        }