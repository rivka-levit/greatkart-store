from django.urls import path
from .views import PlaceOrderView, PaymentView

app_name = 'orders'

urlpatterns = [
    path('place_order/', PlaceOrderView.as_view(), name='place_order'),
    path('payment/', PaymentView.as_view(), name='payment'),
]
