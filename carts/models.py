from django.db import models
from store.models import Product


class Cart(models.Model):
    name = models.CharField(max_length=50, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cart'
        verbose_name_plural = 'carts'

    def __str__(self):
        return self.name


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField()

    class Meta:
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'

    def __str__(self):
        return self.product.product_name
