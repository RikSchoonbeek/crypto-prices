from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=255)
    exchanges = models.ManyToManyField('Exchange')
    type_is_crypto = models.BooleanField()


class TickerSymbol(models.Model):
    symbol = models.CharField(max_length=8)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class Exchange(models.Model):
    name = models.CharField(max_length=255)
