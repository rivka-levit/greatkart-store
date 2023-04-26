from django.shortcuts import redirect, render
from django.views.generic import ListView, View
from .models import CartItem
from .context_processors import get_cart
from django.contrib.auth.mixins import LoginRequiredMixin


class CartView(ListView):
    model = CartItem
    template_name = 'carts/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart = get_cart(self.request)
        return super(CartView, self).get_queryset().filter(cart=cart, is_active=True)


class CheckoutView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        cart = get_cart(self.request)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        return render(request, 'carts/checkout.html', context={
            'cart_items': cart_items
        })


# def add_cart(request, product_id):
#     product = Product.objects.get(id=product_id)
#     cart = get_cart(request)
#     try:
#         cart_item = CartItem.objects.get(product=product, cart=cart)
#         if product.stock > cart_item.quantity:
#             cart_item.quantity += 1
#     except CartItem.DoesNotExist:
#         cart_item = CartItem.objects.create(
#             product=product,
#             cart=cart,
#             quantity=1
#         )
#     cart_item.save()
#     return redirect(request.META['HTTP_REFERER'])

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
