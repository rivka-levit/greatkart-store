from django.views.generic import ListView
from store.models import Product


class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    ordering = ['-created_date']

    def get_queryset(self):
        queryset = super(HomeView, self).get_queryset()
        return queryset.filter(is_available=True)
