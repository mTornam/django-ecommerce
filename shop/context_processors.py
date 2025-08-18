from .cart import Cart
from .models import Category

# def cart(request):
#     if not request.session.session_key:
#         request.session.create()
    
#     session_key = request.session.session_key
#     cart, created = Cart.objects.get_or_create(session_key=session_key)
#     return {'cart': cart}

# def cart(request):
#     if 'cart' not in request.session:
#         cart = request.session['cart'] = {}
#     else:
#         cart = request.session.get('cart')

#     # total_items = sum(item['quantity'] for item in cart.values())
#     count = len(cart)
#     return {'cart': {'items_count': count}}

def cart(request):
    cart = Cart(request)
    count = cart.__len__()
    return {'cart': {'count': count}}

def base_context(request):
    return {
        'categories_list': Category.objects.all().only('name', 'slug') 
    }