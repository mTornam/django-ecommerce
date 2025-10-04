from django.db import models
from shop.models import Product

# Create your models here.
class Order(models.Model):
    Order_Status = [
        ('pending','Pending'),
        ('processing','Processing'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=13)
    address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.CharField(choices=Order_Status, default="pending")
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.SET_DEFAULT, default='UNKNOWN',
                                related_name='order_items')
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