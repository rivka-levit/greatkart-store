from django.db import models
from django.db.models import Avg, Count

from category.models import Category
from accounts.models import Account


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=255, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.product_name

    def average_rating(self):
        reviews = ReviewRating.objects.filter(product=self, status=True)\
            .aggregate(average=Avg('rating'))
        if reviews['average']:
            return float(reviews['average'])
        return None

    def count_reviews(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        if reviews['count']:
            return int(reviews['count'])
        return None


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category='color',
            is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category='size',
            is_active=True
        )


variation_category_choice = (
    ('color', 'color'),
    ('size', 'size')
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    class Meta:
        verbose_name = 'product variation'
        verbose_name_plural = 'product variations'

    def __str__(self):
        return f'{self.variation_category.capitalize()} - ' \
               f'{self.variation_value.capitalize()}'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'review'
        verbose_name_plural = 'reviews'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}: {self.subject}'


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/gallery', max_length=255)

    class Meta:
        verbose_name = 'product gallery'
        verbose_name_plural = 'product galleries'

    def __str__(self):
        return self.product.product_name
