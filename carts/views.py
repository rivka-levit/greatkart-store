from django.views.generic import DetailView, TemplateView
from .models import Cart


class CartView(TemplateView):
    model = Cart
    template_name = 'carts/cart.html'
