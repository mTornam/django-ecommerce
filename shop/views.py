from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import requests

from shop.utils import generate_reference

from .models import Category, Product, Order, OrderItem
# Create your views here.


def home(request):
    featured_categories = Category.objects.all()[:4]
    featured_products = Product.objects.filter(
        available=True).order_by('-created_at')[:8]
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

# ------------------- THIS WHOLE SECTION TO BE MOVED TO ORDER APP ----------------------


# to be moved to order app
def checkout(request):
    from cart.utils import get_cart
    from .forms import ShippingForm, ContactForm
    
    cart = get_cart(request)
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        shipping_form = ShippingForm(request.POST)
        if contact_form.is_valid() and shipping_form.is_valid():
            pass
    else:
        contact_form = ContactForm()
        shipping_form = ShippingForm()

    context = {
        'cart': cart,
        'contact_form': contact_form,
        'shipping_form': shipping_form,
    }
    return render(request, 'cart/checkout.html', context)

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


def get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']

# Not in use LEAVE FOR REFERENCE   
def old_checkout(request):
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
