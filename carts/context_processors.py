from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def get_cart(request):
    cart_id = _cart_id(request)
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=cart_id)
    user = request.user
    if user.id:
        items = CartItem.objects.filter(user=user)
        if items:
            for item in items:
                item.cart = cart
                item.save()
    return cart


def cart_info(request) -> dict:
    if 'admin' in request.path:
        return dict()
    cart = get_cart(request)
    if cart.cart_items:
        return dict(
            cart=cart,
            products_in_cart=[i.product for i in cart.cart_items.all()],
            cart_items_count=cart.cart_items.count()
        )
    return dict(cart=cart, cart_items_count=0)
