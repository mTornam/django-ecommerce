
from decimal import Decimal
from django.shortcuts import get_object_or_404

from shop.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        try:
            product_id = str(product.id)

            if product_id not in self.cart:
                self.cart[product_id] = {
                    'quantity': quantity,
                    'price': str(product.price)
                }
                self.save()
                return True, f'{product.name} added to cart'
            else:
                self.cart[product_id]['quantity'] += 1
                self.save()
                return True, f'{product.name} quantity updated'

        except Exception as e:
            return False, "An error occured"
        
    def _add(self, product, quantity=1):
        status = '' 
        message = ''
        try: 
            product_id = str(product.id)
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': quantity, 'price': str(product.price)}
                status = 'success'
                message = f'{product.name} added to cart.'
            else:
                self.cart[product_id]['quantity'] +=  1
                status = 'info'
                message = f'{product.name} quantity updated.'

            self.save()
            return status, message
        except Exception as e:
            return "Error", "An error occured"

    def _update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity

            self.save()

    def update(self, product_id, quantity):
        try:
            product_id = str(product_id)
            if product_id in self.cart:
                self.cart[product_id]['quantity'] = quantity
                self.save()

                return True, 'Item quantity updated'
            else:
                return False, 'Item not found in Cart'

        except Exception as e:
            return False, f'An error occurred: {e}'

    def _remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]

            self.save()

    def remove(self, product_id):
        try:
            product_id = str(product_id)

            if product_id in self.cart:
                del self.cart[product_id]
                self.save()
                return True, f'Item removed from cart'
            else:
                return False, f'product id not in cart'

        except Exception as e:
            return False, f'An error occurred: {e}'

    def clear(self):
        del self.session['cart']
        self.save()

    def save(self):
        self.session.modified = True

    @property
    def total(self):
        total = Decimal('0.00')

        for item in self.cart.values():
            price = Decimal(item['price'])
            quantity = item['quantity']
            total += price * quantity

        return round(float(total), 2)

    def __iter__(self):
        for product_id, item in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
                yield {
                    'product': product,
                    'product_id': product_id,
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'total_price': round(float(item['price']) * item['quantity'], 2)
                }
            except:
                continue

    def __len__(self):
        return len(self.cart)

    def get_product_total(self, product_id):
        product = self.cart.get(str(product_id))
        if product:
            return round(float(product['price']) * product['quantity'], 2)
        return 0
