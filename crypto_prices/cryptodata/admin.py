from django.contrib import admin

from .models import Currency, CurrencyExchangePK, Exchange, TickerSymbol


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(CurrencyExchangePK)
class CurrencyExchangePKAdmin(admin.ModelAdmin):
    pass


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    pass


@admin.register(TickerSymbol)
class TickerSymbolAdmin(admin.ModelAdmin):
    pass
