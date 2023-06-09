
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, DetailView
import datetime
import json
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from carts.models import CartItem
from carts.views import get_cart
from store.models import Product

from .models import Order, Payment, OrderProduct
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
            data.sub_total = cart.total_cart()
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

            # Send order number to Payment View
            request.session['order_number'] = order_number

            return redirect('orders:payment')

        messages.error(self.request, 'Invalid delivery information!')
        return redirect(request.META.get('HTTP_REFERER'))


class PaymentView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        try:
            order_number = request.session.get('order_number')
            order = Order.objects.get(user=request.user,
                                      is_ordered=False,
                                      order_number=order_number)
        except Order.DoesNotExist:
            messages.error(request, 'You have not placed any order yet!')
            return redirect('cart:detail')

        cart_items = CartItem.objects.filter(user=request.user)
        return render(self.request, 'orders/payment.html', context={
            'order': order,
            'cart_items': cart_items
        })

    def post(self, request):
        body = json.loads(self.request.body)
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

        # Store transaction details inside Payment model
        payment = Payment(
            user=self.request.user,
            payment_id=body['transID'],
            payment_method=body['payment_method'],
            amount_paid=order.total,
            status=body['status']
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.payment = payment
            order_product.user = request.user
            order_product.product = item.product
            order_product.is_ordered = True
            order_product.product_price = item.product.price
            order_product.quantity = item.quantity
            order_product.save()

            product_variations = item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variations)
            order_product.save()

            # Reduce the quantity of the sold product
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send email to the customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_received_email.html', {
            'user': self.request.user,
            'order': order
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # Send order number and transaction id back to js script
        data = {
            'order_number': order.order_number,
            'trans_id': payment.payment_id
        }

        return JsonResponse(data)


class OrderCompleteView(TemplateView):
    template_name = 'orders/order_complete.html'

    def get_context_data(self, **kwargs):
        context = super(OrderCompleteView, self).get_context_data(**kwargs)
        order_number = self.request.GET.get('order_number')
        transaction = self.request.GET.get('transaction')
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        context['order_number'] = order.order_number
        context['payment'] = Payment.objects.get(payment_id=transaction)
        context['order'] = order
        context['order_products'] = OrderProduct.objects.filter(order=order)
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order_id = self.kwargs.get('pk')
        order = Order.objects.get(id=order_id)
        context['order_products'] = OrderProduct.objects.filter(order=order)
        return context
