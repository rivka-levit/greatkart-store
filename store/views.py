from django.views.generic import ListView, View
from .models import Product
from category.models import Category
from django.shortcuts import get_object_or_404, render


class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['id']

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


class ProductDetailView(View):
    def get(self, request, category_slug, product_slug):
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        context = {
            'product': product
        }
        return render(request, 'store/product-detail.html', context)


class SearchResultsView(ListView):
    model = Product
    template_name = 'store/search-result.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['id']

    def get_queryset(self):
        products = super(SearchResultsView, self).get_queryset().filter(is_available=True)
        query = self.request.GET.get("q")
        if not query:
            return None
        return products.filter(product_name__contains=query)
