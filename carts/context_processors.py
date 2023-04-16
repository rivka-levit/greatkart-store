from .models import Cart


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


def cart_items_count(request) -> dict:
    cart = _get_cart(request)
    if cart.cart_items:
        return dict(cart=cart, count=cart.cart_items.count())
    return dict(cart=cart, count=0)
