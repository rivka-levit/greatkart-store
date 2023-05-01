from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
import datetime
from django.contrib import messages

from carts.models import CartItem
from carts.views import get_cart

from .models import Order
from .forms import OrderForm


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
        cart = get_cart(self.request)
        form = OrderForm(self.request.POST)
        if form.is_valid():
            data = Order()
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.user = self.request.user
            data.total = cart.grand_total_cart()
            data.tax = cart.tax_cart()
            data.ip = self.request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            dt = datetime.date.today()
            current_date = dt.strftime('%Y%m%d')
            order_number = f'{current_date}{data.id}'
            data.order_number = order_number
            data.save()
            return redirect(request.META.get('HTTP_REFERER'))
        messages.error(self.request, 'Invalid delivery information!')
        return redirect(request.META.get('HTTP_REFERER'))
