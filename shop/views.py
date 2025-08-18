import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import requests

from shop.utils import generate_reference

from .cart import Cart
from .models import Category, Product, ProductImage, Order, OrderItem
from .forms import CheckoutForm
# Create your views here.


def home(request):
    featured_categories = Category.objects.all()[:4]
    featured_products = Product.objects.filter(
        available=True).order_by('-created')[:8]
    return render(request, 'shop/home.html', {
        'featured_categories': featured_categories,
        'featured_products': featured_products,
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'shop/categories.html', {'categories': categories})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/products.html', {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'query': query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    images = product.images.all()
    related_products = Product.objects.filter(
        category=product.category, available=True).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'images': images,
        'related_products': related_products,
    })


def get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def cart_detail(request):
    cart = Cart(request)
    cart_total = cart.total

    return render(request, 'shop/cart.html', {
        'cart_items': cart,
        'cart_total': cart_total
    })


def _cart_add(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)

        quantity = data.get('quantity')
        if quantity:
            success, message = cart.add(product=product, quantity=quantity)
        else:
            success, message = cart.add(product=product)

        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.__len__()
            })
        else:
            return JsonResponse({'success': False, 'message': message}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
def cart_add(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)

    qty = data.get('quantity')
    if qty: status, msg = cart._add(product, qty)
    else: status, msg = cart._add(product)

    if status != "error":
        return JsonResponse({
            'success': True,
            'type': status,
            'message': msg,
            'cart_count': cart.__len__()
        })
    else:
        return JsonResponse({'success': False, 'message': msg}, status=400)



def cart_update(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity'))
        cart = Cart(request)
        success, message = cart.update(
            product_id=product_id, quantity=quantity)

        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.__len__(),
                'product_total': cart.get_product_total(product_id),
                'cart_total': cart.total
            })
        else:
            return JsonResponse({'success': False, 'message': message}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def cart_remove(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        cart = Cart(request)
        success, message = cart.remove(product_id=product_id)

        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.__len__(),
                'cart_total': cart.total
            })
        else:
            return JsonResponse({'success': False, 'message': message}, status=400)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    

def cart_clear(request):
    cart = Cart(request)
    cart.clear()

    return redirect('shop:cart_detail')


def checkout(request):
    cart = get_cart(request)

    cart_items = []
    total_price = 0

    for product_id, item_data in cart.items():
        product = Product.objects.get(id=product_id)
        quantity = item_data['quantity']
        price = float(item_data['price'])
        total = quantity * price
        total_price += total

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'total': total
        })

    if not cart_items:
        messages.warning(request, "Your Cart is empty!")
        return redirect('shop:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
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

            # Add items to order
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item[product],
                    price=item[price],
                    quantity=item[quantity],
                )

            # clear cart from session
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(
                request, "Your order has been placed successfully!")
            return render(request, 'shop/checkout.html', {'order': order})
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    })

# Payment Section
@csrf_exempt
def initiate_paystack_checkout(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        amount = round(float(request.POST.get('amount')) * 100, 2)
        name = request.POST.get('name') 

        reference = generate_reference()

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SK}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": amount,
            "currency": "GHS",
            "reference": reference,
            "callback_url": "",
            "metadata": {
                "custom_fields": [
                    {
                        "display_name": "Full Name",
                        "variable_name": "full_name",
                        "value": name
                    }
                ]
            }            
        }

        response = requests.post("https://api.paystack.co/transaction/initialize",
                                 json=payload, headers=headers)

        data = response.json()
        print(data)
        if data.get('status'):
            checkout_url = data['data']['authorization_url']
            return redirect(checkout_url)
        return JsonResponse({'error': 'Failed to initiate payment'}, status=400)

def payment_callback(request):
    # Optionally verify payment here using Paystack's verify endpoint
    return HttpResponse("Payment complete!")
