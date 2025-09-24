# shop/forms.py
from django import forms
from .models import Order

# class CheckoutForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'payment_method']
#         widgets = {
#             'payment_method': forms.RadioSelect(choices=Order.PAYMENT_METHODS),
#         }


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)
    email = forms.EmailField()
    # phone = forms.CharField(max_length=10, min_length=10)


class ShippingForm(forms.Form):
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup from store'),
        ('delivery', 'Delivery'),
    ]

    CITY_CHOICES = [
        ('accra', 'Accra'),
        ('tema', 'Tema'),
    ]

    street_address = forms.CharField(max_length=120)
    city = forms.ChoiceField(choices=CITY_CHOICES)
    delivery = forms.ChoiceField(choices=DELIVERY_CHOICES, widget=forms.RadioSelect)

