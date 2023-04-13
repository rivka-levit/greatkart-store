from django.urls import path
from .views import StoreView

app_name = 'store'

urlpatterns = [
    path('', StoreView.as_view(), name='all_products'),
    path('<slug:category_slug>/', StoreView.as_view(), name='by_category')
]
