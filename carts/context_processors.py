from .views import get_cart


def cart_info(request) -> dict:
    if 'admin' in request.path:
        return dict()
    cart = get_cart(request)
    if cart.cart_items:
        return dict(
            cart=cart,
            cart_items_count=cart.cart_items.count()
        )
    return dict(cart=cart, cart_items_count=0)
