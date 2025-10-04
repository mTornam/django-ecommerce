from django import forms
from .models import Order

class ContactForm(forms.Form):
    # first_name = forms.CharField(max_length=25)
    # last_name = forms.CharField(max_length=25)
    name = forms.CharField(max_length=200)
    email = forms.EmailField()
    phone = forms.CharField(min_length=10, max_length=13)


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

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'address', 'phone']