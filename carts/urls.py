from django.urls import path
from .views import CartView, add_cart, remove_item, decrement_item

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='detail'),
    path('add_cart/<int:product_id>', add_cart, name='add_cart'),
    path('remove_item/<int:item_id>', remove_item, name='remove_item'),
    path('decrement_item/<int:item_id>', decrement_item, name='decrement_item'),
]
