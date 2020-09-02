from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


# Create your models here.
class PlaidItem(models.Model):
    item_id = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    institution_name = models.CharField(max_length=200)
    institution_id = models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(),
                             related_name='item',
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item_id', 'access_token'], name="item-access")
        ]

    def get_absolute_url(self):
        return reverse('item:item_account_list', args=[self.id])


class PlaidAccount(models.Model):
    account_id = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    official_name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=50)
    subtype = models.CharField(max_length=50)
    mask = models.CharField(max_length=50)
    item = models.ForeignKey(PlaidItem,
                             related_name='accounts',
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['account_id', 'item_id'], name="link-account")
        ]

    def get_absolute_url(self):
        return reverse('item:account_detail', args=[self.item.id, self.id])


class PlaidTransaction(models.Model):
    account = models.ForeignKey(PlaidAccount,
                                related_name='transactions',
                                on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    iso_currency_code = models.CharField(max_length=10)
    category = models.CharField(max_length=100, null=True)
    category_id = models.CharField(max_length=100, null=True)
    date = models.DateTimeField()
    name = models.CharField(max_length=100)
    pending = models.BooleanField()
    pending_transaction_id = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=100, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['transaction_id', 'account_id'], name="account-transaction")
        ]
