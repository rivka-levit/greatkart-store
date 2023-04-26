from django.db import models
from store.models import Product, Variation
from accounts.models import Account


class Cart(models.Model):
    cart_id = models.CharField(max_length=50, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cart'
        verbose_name_plural = 'carts'

    def __str__(self):
        return str(self.cart_id)

    def total_cart(self):
        if self.cart_items:
            return sum([item.total_item() for item in self.cart_items.all()])

    def tax_cart(self):
        if self.cart_items:
            return 2 * self.total_cart() / 100

    def grand_total_cart(self):
        if self.cart_items:
            return self.total_cart() + self.tax_cart()


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, related_name='cart_items')
    quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'

    def __str__(self):
        return str(self.product.product_name)

    def total_item(self):
        return self.quantity * self.product.price
