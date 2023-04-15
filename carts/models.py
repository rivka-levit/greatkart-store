from django.db import models
from store.models import Product


class Cart(models.Model):
    cart_id = models.CharField(max_length=50, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cart'
        verbose_name_plural = 'carts'

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, related_name='cart_items')
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'

    def __str__(self):
        return self.product.product_name
