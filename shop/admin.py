# shop/admin.py
from django.contrib import admin
from .models import (Category, Product, ProductImage, Order, OrderItem)



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 4

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available']
    list_filter = ['available', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'total_paid', 'status', 'created']
    list_filter = ['status', 'created']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    inlines = [OrderItemInline]