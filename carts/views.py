from django.shortcuts import redirect
from django.views.generic import ListView
from .models import Cart, CartItem
from store.models import Product


class CartView(ListView):
    model = CartItem
    template_name = 'carts/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated is False:
            cart = _get_cart(self.request)
            cart_items = super(CartView, self).get_queryset().filter(cart=cart)
        return cart_items


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def _get_cart(request):
    cart_id = _cart_id(request)
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=cart_id)
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = _get_cart(request)
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
