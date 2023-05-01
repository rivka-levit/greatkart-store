from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from carts.models import CartItem
from carts.views import get_cart


class PlaceOrderView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        if CartItem.objects.filter(user=self.request.user).count() <= 0:
            return redirect('store:all_products')

        cart = get_cart(self.request)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        return render(request, 'orders/place_order.html', context={
            'cart_items': cart_items
        })

    def post(self, request):
        pass
