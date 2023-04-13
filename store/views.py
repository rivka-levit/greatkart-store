from django.views.generic import ListView
from .models import Product
from category.models import Category
from django.shortcuts import get_object_or_404


class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'

    def get_queryset(self):
        products = super(StoreView, self).get_queryset().filter(is_available=True)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products_count'] = self.get_queryset().count()
        return context
