from django.urls import path
from .views import CartView, add_cart

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='detail'),
    path('add_cart/<int:product_id>', add_cart, name='add_cart')
]
