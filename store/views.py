from django.views.generic import ListView
from .models import Product
from category.models import Category


class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'GreatKart | One of the Biggest Online Shopping Platform'
        context['categories'] = Category.objects.all()
        context['products_count'] = self.get_queryset().count()
        return context
