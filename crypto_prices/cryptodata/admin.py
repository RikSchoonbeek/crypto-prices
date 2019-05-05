from django.contrib import admin

from .models import CryptoCurrency, Exchange, TickerSymbol


@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    pass


@admin.register(TickerSymbol)
class TickerSymbolAdmin(admin.ModelAdmin):
    pass
