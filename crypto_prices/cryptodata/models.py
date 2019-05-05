from django.db import models


class CryptoCurrency(models.Model):
    name = models.CharField(max_length=255)
    exchanges = models.ManyToManyField('Exchange')


class TickerSymbol(models.Model):
    symbol = models.CharField(max_length=8)
    crypto = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)


class Exchange(models.Model):
    name = models.CharField(max_length=255)
