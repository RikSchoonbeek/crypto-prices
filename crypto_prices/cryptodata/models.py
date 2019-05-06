from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=255)
    exchanges = models.ManyToManyField('Exchange')
    type_is_crypto = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'type_is_crypto']


class CurrencyExchangePK(models.Model):
    KEY_TYPE_CHOICES = (
        ('STR', 'string'),
        ('INT', 'integer'),
    )

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    exchange = models.ForeignKey('Exchange', on_delete=models.CASCADE)
    key = models.CharField(max_length=63)
    key_type = models.CharField(
        max_length=3, choices=KEY_TYPE_CHOICES, default='STR')

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']


class TickerSymbol(models.Model):
    symbol = models.CharField(max_length=8)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    def __str__(self):
        return self.symbol

    class Meta:
        ordering = ['symbol']


class Exchange(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
