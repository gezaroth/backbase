from exchange.models import CurrencyExchangeRate
from .base_provider import BaseProvider
import logging

class LocalExchangeRateProvider(BaseProvider):

    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date=None):
        """Fetches the most recent exchange rate."""
        try:
            if valuation_date is None:
                # Fetch the latest available rate
                valuation_date = CurrencyExchangeRate.objects.filter(
                    source_currency__code=source_currency,
                    exchanged_currency__code=exchanged_currency
                ).order_by('-valuation_date').first().valuation_date

            rate = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                exchanged_currency__code=exchanged_currency,
                valuation_date=valuation_date
            ).first()

            if rate:
                return {
                    'rate_value': rate.rate_value,
                    'valuation_date': rate.valuation_date.isoformat(),
                    'provider': 'LocalProvider'
                }
            logging.warning(f"No local rate found for {source_currency}/{exchanged_currency} on {valuation_date}.")
            return None
        except Exception as e:
            logging.error(f"Error fetching local exchange rate: {e}")
            return None

    def get_historical_rates(self, source_currency, exchanged_currency, start_date):
        """Fetches historical exchange rates starting from a given date."""
        rates = CurrencyExchangeRate.objects.filter(
            source_currency__code=source_currency,
            exchanged_currency__code=exchanged_currency,
            valuation_date__gte=start_date
        ).order_by('valuation_date')

        return [
            {
                'rate_value': rate.rate_value,
                'valuation_date': rate.valuation_date.isoformat(),
                'provider': 'LocalProvider'
            } for rate in rates
        ]

    def calculate_twr(self, source_currency, exchanged_currency, amount, start_date, cash_flows):
        """Implements Time-Weighted Return (TWR) calculation."""
        historical_rates = self.get_historical_rates(source_currency, exchanged_currency, start_date)
        twr_values = []
        previous_balance = amount

        for cash_flow in cash_flows:
            flow_date = cash_flow['date']
            flow_amount = cash_flow['amount']
            rate_value = next((rate['rate_value'] for rate in historical_rates if rate['valuation_date'] <= flow_date), None)
            
            if rate_value is not None:
                previous_balance *= (1 + (rate_value - 1))
            
            previous_balance += flow_amount
            twr_values.append(previous_balance)

        final_twr = 1
        for rate in historical_rates:
            final_twr *= (1 + (rate['rate_value'] - 1))

        final_twr -= 1
        return {'final_twr': final_twr, 'twr_values': twr_values}
