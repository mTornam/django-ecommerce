import requests
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.shortcuts import render, redirect
from django.conf import settings

from .models import Order, OrderItem, Payment
from .forms import OrderForm
from shop.utils import generate_reference
from cart.utils import get_cart


PAYSTACK_SECRET_KEY = settings.PAYSTACK_SK
PAYSTACK_BASE_URL = "https://api.paystack.co"

# Create your views here.
@transaction.atomic
def checkout(request):
    cart = get_cart(request)
    order_id = request.session.get('order_id')
    order = None
    payment = None

    if not cart.get_count > 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('shop:home')

    # Check if there's an existing pending order for this session
    if order_id:
        try:
            order = Order.objects.get(id=order_id, status='pending')
            payment = Payment.objects.get(order=order, status='pending')
        except (Order.DoesNotExist, Payment.DoesNotExist):
            # If order/payment is not found or not pending, clear session
            order = None
            payment = None
            request.session.pop('order_id', None)
            request.session.pop('payment_id', None)

    # Populate form with existing order data if available
    initial_data = {}
    if order:
        initial_data = {
            'full_name': order.full_name,
            'email': order.email,
            'address': order.address,
            'phone': order.phone,
        }

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order_total = cart.get_total

            # If a pending order exists, update it. Otherwise, create a new one.
            if order and payment:
                order.full_name = form.cleaned_data['full_name']
                order.email = form.cleaned_data['email']
                order.address = form.cleaned_data['address']
                order.phone = form.cleaned_data['phone']
                order.total_price = order_total
                order.save()
            else:
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
            # If form is invalid, show errors on the page
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm(initial=initial_data)

    context = {'cart': cart, 'form': form}
    return render(request, 'order/checkout.html', context)


# url : 'pay_init'
def paystack_init(request):
    order_id = request.session.get('order_id')
    payment_id = request.session.get('payment_id')

    if not order_id or not payment_id:
        messages.error(request, "No order found to make a payment.")
        return redirect('checkout')

    try:
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(id=payment_id)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        messages.error(request, "Order or Payment not found. Please try again.")
        # Clear stale session data
        request.session.pop('order_id', None)
        request.session.pop('payment_id', None)
        return redirect('shop:home')

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
            "reference": payment.reference,
            "callback_url": request.build_absolute_uri(reverse('verify_pay')),
        }
        response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers).json()

        if response.get('status'):
            auth_url = response['data']['authorization_url']
            return redirect(auth_url)
        else:
            messages.error(request, f"Payment initialization failed: {response.get('message')}")
            return redirect('pay_init')

    return render(request, 'order/pay.html', {'amount': order.total_price, 'email': email})

# url : 'verify_pay'    
@transaction.atomic
def verify_payment(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, "Payment reference not found.")
        return redirect('checkout')
    try:
        payment = Payment.objects.get(reference=reference)
        order = payment.order
    except Payment.DoesNotExist:
        messages.error(request, "Payment not found for this reference.")
        return redirect('checkout')

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers).json()

    if response.get('data', {}).get('status') == 'success':
        # Migrate cart items to order items and clear cart
        cart = get_cart(request)

        # Use bulk_create for efficiency
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
            for item in cart.items.all()
        ]
        OrderItem.objects.bulk_create(order_items)

        order.status = 'processing'
        order.save()

        cart.items.all().delete()  # clear cart

        payment.status = 'paid'
        payment.save()

        # Clear session data
        request.session.pop('order_id', None)
        request.session.pop('payment_id', None)

        messages.success(request, 'Payment successful')
        return redirect('shop:home')
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Payment verification failed. Please try again.')
        # Redirect back to the payment page to allow retry
        return redirect('pay_init')

    
