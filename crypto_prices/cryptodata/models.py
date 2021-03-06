from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=255)
    ticker_symbol = models.CharField(max_length=8)
    exchanges = models.ManyToManyField('Exchange')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'ticker_symbol']


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
        unique_together = [['exchange', 'key']]


# class TickerSymbol(models.Model):
#     symbol = models.CharField(max_length=8)
#     currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.symbol

#     class Meta:
#         ordering = ['symbol']
#         unique_together = [['symbol', 'currency']]


class TradingPair(models.Model):
    currency1 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='currency1')
    currency2 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='currency2')
    exchanges = models.ManyToManyField('Exchange')

    def __str__(self):
        currency1_name = self.currency1.name
        currency2_name = self.currency2.name
        return f"{currency1_name} - {currency2_name}"


class TradingPairExchangePK(models.Model):
    KEY_TYPE_CHOICES = (
        ('STR', 'string'),
        ('INT', 'integer'),
    )

    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    exchange = models.ForeignKey('Exchange', on_delete=models.CASCADE)
    key = models.CharField(max_length=63)
    key_type = models.CharField(
        max_length=3, choices=KEY_TYPE_CHOICES, default='STR')

    def __str__(self):
        return self.key + " - " + self.exchange.name

    class Meta:
        ordering = ['key']


class Exchange(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
