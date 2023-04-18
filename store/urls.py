from django.urls import path
from .views import StoreView, ProductDetailView, SearchResultsView

app_name = 'store'

urlpatterns = [
    path('', StoreView.as_view(), name='all_products'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('<slug:category_slug>/', StoreView.as_view(), name='by_category'),
    path('<slug:category_slug>/<slug:product_slug>/',
         ProductDetailView.as_view(), name='product_detail'),
]
