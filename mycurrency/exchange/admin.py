from django.contrib import admin
from .models import Currency, CurrencyExchangeRate

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')

@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('source_currency', 'exchanged_currency', 'valuation_date', 'rate_value')
