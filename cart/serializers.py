from rest_framework import serializers
from .models import Cart, CartItem
from shop.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Retrieve, update or remove cart item"""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "subtotal",
        ]
        extra_kwargs = {"product": {"read_only": True}}

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price


class CartSerializer(serializers.ModelSerializer):
    """ """

    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total", "count"]

    def get_total(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())

    def get_count(self, obj):
        return obj.items.count()


class AddCartItemSerializer(serializers.Serializer):
    """Add item to cart"""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, initial=1)
