from django.views.generic import ListView
from store.models import Product


class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super(HomeView, self).get_queryset()
        return queryset.filter(is_available=True)

    # def paginate_queryset(self):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'GreatKart | One of the Biggest Online Shopping Platform'
        return context
