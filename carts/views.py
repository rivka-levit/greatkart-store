from django.shortcuts import redirect
from django.views.generic import ListView
from .models import CartItem, Cart


class CartView(ListView):
    model = CartItem
    template_name = 'carts/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart = get_cart(self.request)
        cart_items = super(CartView, self).get_queryset().filter(cart=cart, is_active=True)
        return cart_items


def _cart_id(request):
    try:
        cart = request.session.session_key
    except:
        cart = request.session.create()
    return cart


def get_cart(request):
    cart_id = _cart_id(request)
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=cart_id)
    user = request.user
    if user.is_authenticated:
        items = CartItem.objects.filter(user=user)
        if items:
            for item in items:
                item.cart = cart
                item.save()
    return cart


def increment_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    product = item.product
    if product.stock > item.quantity:
        item.quantity += 1
        item.save()
    return redirect(request.META['HTTP_REFERER'])


def decrement_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart:detail')


def remove_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.delete()
    return redirect(request.META['HTTP_REFERER'])
