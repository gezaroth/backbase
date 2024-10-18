from django.urls import path
from .views import (
    get_exchange_rates_for_date_range,
    latast_exchange_rate,
    calculate_twr,
    currency_converter_view,
    graph_view,
)

urlpatterns = [
    path('get-exchange-rates/', get_exchange_rates_for_date_range, name='get-rates-dates-range'),
    path('convert/', latast_exchange_rate, name='convert-currency'),
    path('get-twr/', calculate_twr, name='get-twr'),

    path('currency-converter/', currency_converter_view, name='currency_converter_view'),
    path('graph/', graph_view, name='graph'),
]
