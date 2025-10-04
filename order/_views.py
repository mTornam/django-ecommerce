import requests 
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect, render
from cart.utils import get_cart
from shop.models import Product
from forms import ShippingForm, ContactForm, OrderForm

from shop.utils import generate_reference

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SK
PAYSTACK_BASE_URL = "https://api.paystack.co"


from django.db import  models

# models
class Order(models.Model):
    Order_Status = [
        ('pending','Pending'),
        ('processing','Processing'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(min_length=10, max_length=13)
    address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.CharField(choices=Order_Status, default="pending")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.SET_DEFAULT, default='UNKNOWN')
    quantity = models.PositiveIntegerField()


class Payment(models.Model):
    Payment_Status = [
        ('pending','Pending'),
        ('paid','Paid'),
        ('failed','Failed'),
        ('cancelled','Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.PROTECT)
    status = models.CharField(choices=Payment_Status, default='pending')
    reference = models.CharField()

# views
def checkout(request):
    cart = get_cart(request)
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order_total = cart.get_total()
            order = Order.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                total_price=order_total
            )
            payment = Payment.objects.create(
                order=order,
                reference=generate_reference()
            )
            # Store IDs in session
            request.session['order_id'] = order.id
            request.session['payment_id'] = payment.id
            return redirect('pay_init')
        else:
            return JsonResponse({'error': "Invalid form data"})
    form = OrderForm()
    context = {'cart': cart, 'form': form}
    return render(request, 'order/checkout.html', context)

# url : 'pay_init'
def paystack_init(request):
    order_id = request.session.get('order_id')
    payment_id = request.session.get('payment_id')
    if not order_id or not payment_id:
        return redirect('checkout')
    order = Order.objects.get(id=order_id)
    payment = Payment.objects.get(id=payment_id)
    email = order.email
    amount = int(order.total_price * 100)  # Convert to pesewas

    if request.method == "POST":
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "amount": amount,
            "currency": "GHS",
            "callback_url": request.build_absolute_uri(reverse('verify_pay')),
        }
        response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers).json()
        if response.get('status'):
            auth_url = response['data']['authorization_url']
            return redirect(auth_url)
        return JsonResponse({'error': "Payment initialization failed"})
    return render(request, 'order/pay.html', {'amount': order.total_price, 'email': email})
    
# url : 'verify_pay'    
def verify_payment(request):
    reference = request.GET.get('reference')
    payment_id = request.session.get('payment_id')
    if not payment_id or not reference:
        return redirect('checkout')
    try:
        payment = Payment.objects.get(pk=payment_id, reference=reference)
    except Payment.DoesNotExist:
        return JsonResponse({'error': "Payment not found"})
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers).json()
    if response.get('status'):
        # Migrate cart items to order items and clear cart
        cart = get_cart(request)
        # ... migrate logic here ...
        order_id = request.session.get('order_id')
        order = Order.objects.get(id=order_id)

        for item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
            order_item.save()

        cart.items.all().delete() # cleare cart

        payment.status = 'paid'
        payment.save()
        return redirect('shop:home')
    else:
        payment.status = 'failed'
        payment.save()
        return JsonResponse({'error': "Payment verification failed"})