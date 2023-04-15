from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView, ListView
from .models import Cart, CartItem
from store.models import Product
from django.http import HttpResponseRedirect


class CartView(ListView):
    model = CartItem
    template_name = 'carts/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated is False:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(self.request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(self.request))
            cart_items = super(CartView, self).get_queryset().filter(cart=cart)
        return cart_items


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
    cart_item.save()
    return redirect('cart:detail')
