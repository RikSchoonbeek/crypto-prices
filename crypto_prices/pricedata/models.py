from django.db import models
from cryptodata.models import Currency, Exchange


class ExchangeRate(models.Model):
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='currency')
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=40, decimal_places=20)
    ask = models.DecimalField(max_digits=40, decimal_places=20)
    base = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='base')
    quote = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='quote')
    timestamp = models.DateTimeField(auto_now_add=True)
