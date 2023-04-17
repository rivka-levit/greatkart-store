from django.shortcuts import redirect
from django.views.generic import ListView
from .models import CartItem
from store.models import Product
from .context_processors import _get_cart


class CartView(ListView):
    model = CartItem
    template_name = 'carts/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated is False:
            cart = _get_cart(self.request)
            cart_items = super(CartView, self).get_queryset().filter(cart=cart, is_active=True)
        return cart_items


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = _get_cart(request)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
    cart_item.save()
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
