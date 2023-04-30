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


