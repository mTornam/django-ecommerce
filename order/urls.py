from django.urls import path
from . import views

urlpatterns = [
    path('checkout', views.checkout, name='checkout'),
    path('pay', views.paystack_init, name='pay_init'),
    path('payment/verification', views.verify_payment, name='verify_pay'),
]