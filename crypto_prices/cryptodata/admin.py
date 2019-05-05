from django.contrib import admin

from .models import Currency, Exchange, TickerSymbol


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    pass


@admin.register(TickerSymbol)
class TickerSymbolAdmin(admin.ModelAdmin):
    pass
