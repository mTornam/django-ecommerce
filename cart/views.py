from rest_framework.response import Response
from rest_framework import status, generics
from .models import Cart, CartItem
from .serializers import CartSerializer, AddCartItemSerializer, CartItemSerializer

# Create your views here.
class CartView(generics.GenericAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET" or self.request.method == "DELETE":
            return CartSerializer
        elif self.request.method == "POST":
            return AddCartItemSerializer

    def get_cart(self):
        """Centralized cart retrieval logic"""
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
        else:
            if not self.request.session.session_key:
                self.request.session.create()
            session_key = self.request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def get(self, request):
        cart = self.get_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_cart()
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity  
            cart_item.save()

        # Return consistent response with cart data
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = self.get_cart()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

def get_cart(request):
    """Centralized cart retrieval logic"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart    

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart = get_cart(self.request)
        return CartItem.objects.filter(cart=cart)