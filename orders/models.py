from django.db import models
from accounts.models import Account


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True,
                             related_name='orders')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    total = models.DecimalField(decimal_places=2)
    tax = models.DecimalField(decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='New')
    ip = models.CharField(max_length=20, blank=True)
    order_note = models.CharField(max_length=100, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} -- Order number: {self.order_number}'
