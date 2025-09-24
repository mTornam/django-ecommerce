from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view()),
    path('items/<int:pk>', views.CartItemDetailView.as_view()),
]