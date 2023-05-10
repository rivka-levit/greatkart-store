from django.views.generic import ListView, View
from carts.views import get_cart
from .models import Product, Variation, ReviewRating
from .forms import ReviewForm
from category.models import Category
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from carts.models import CartItem
from django.contrib import messages


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
        reviews = ReviewRating.objects.filter(product=product)
        context = {
            'product': product,
            'reviews': reviews
        }
        return render(request, 'store/product-detail.html', context)

    def post(self, request, category_slug, product_slug):
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)

        # Handle reviews
        if request.POST.get('review_submitted'):
            return self.__review_rating(self.request, product)

        # Adding product to the cart
        product_variations = list()
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(product=product,
                                                  variation_category__iexact=key,
                                                  variation_value__iexact=value)
                product_variations.append(variation)
            except:
                pass

        cart = get_cart(request)
        if CartItem.objects.filter(product=product, cart=cart).exists():
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            if any(sorted(product_variations,
                          key=lambda x: x.variation_category) ==
                   sorted(list(x.variations.all()),
                          key=lambda y: y.variation_category) for x in cart_items):
                for i in cart_items:
                    if sorted(product_variations,
                              key=lambda x: x.variation_category) == \
                        sorted(list(i.variations.all()),
                               key=lambda x: x.variation_category):
                        item = CartItem.objects.get(product=product, id=i.id)
                        break
            else:
                item = CartItem.objects.create(product=product, cart=cart)
                if product_variations:
                    item.variations.add(*product_variations)
        else:
            item = CartItem.objects.create(product=product, cart=cart)
            if product_variations:
                item.variations.add(*product_variations)
        user = request.user
        if user.is_authenticated:
            item.user = user
        item.quantity += 1
        item.save()

        return redirect(self.request.META['HTTP_REFERER'])

    @staticmethod
    def __review_rating(request, product):
        try:
            review = ReviewRating.objects.get(product_id=product.id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.product = product
                data.user = request.user
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
        return redirect(request.META.get('HTTP_REFERER'))


class SearchResultsView(ListView):
    model = Product
    template_name = 'store/search-result.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['-created_date']

    def get_queryset(self):
        products = super(SearchResultsView, self).get_queryset().filter(is_available=True)
        query = self.request.GET.get("q")
        if not query:
            return None
        return products.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products_count'] = self.get_queryset().count()
        context['query'] = self.request.GET.get("q")
        return context
