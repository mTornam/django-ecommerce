from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add', views.cart_add, name='cart_add'),
    path('cart/remove', views.cart_remove, name='cart_remove'),
    path('cart/update', views.cart_update, name='cart_update'),
    path('cart/clear', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
    path('pay/', views.initiate_paystack_checkout, name='paystack_checkout'),

]
