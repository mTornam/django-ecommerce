import json
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .models import Product, Order, OrderItem
from .forms import CheckoutForm
from .utils import generate_reference
from .cart import Cart


def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)
    total_price = cart.total

    if not cart_items:
        messages.warning(request, "Your cart is empty!")
        return redirect('shop:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                payment_method=form.cleaned_data['payment_method'],
                total_paid=total_price,
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            reference = generate_reference()
            request.session['reference'] = reference
            request.session['order_id'] = order.id

            return redirect('shop:initiate_paystack_checkout')
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    })


@csrf_exempt
def initiate_paystack_checkout(request):
    order_id = request.session.get('order_id')
    reference = request.session.get('reference')
    order = get_object_or_404(Order, id=order_id)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SK}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": order.email,
        "amount": int(order.total_paid * 100),
        "currency": "GHS",
        "reference": reference,
        "callback_url": "https://yourdomain.com/payment/callback/",
        "metadata": {
            "custom_fields": [
                {
                    "display_name": "Full Name",
                    "variable_name": "full_name",
                    "value": f"{order.first_name} {order.last_name}"
                }
            ]
        }
    }

    response = requests.post("https://api.paystack.co/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if data.get('status'):
        return redirect(data['data']['authorization_url'])

    return JsonResponse({'error': 'Payment initiation failed'}, status=400)


@csrf_exempt
def payment_callback(request):
    reference = request.GET.get('reference')
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SK}"
    }

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    result = response.json()

    if result.get('status') and result['data']['status'] == 'success':
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        order.paid = True
        order.save()

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, "Payment successful! Your order has been placed.")
    else:
        messages.error(request, "Payment verification failed.")

    return redirect('shop:cart_detail')
