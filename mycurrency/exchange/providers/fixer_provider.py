import requests
from datetime import datetime, timedelta
import logging
from .base_provider import BaseProvider
from exchange.models import CurrencyExchangeRate

class FixerProvider(BaseProvider):
    BASE_URL = 'http://data.fixer.io/api'

    def __init__(self, access_key):
        self.access_key = access_key

    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date=None):
        """Fetches the exchange rate for a specific date."""
        endpoint = f"{self.BASE_URL}/{valuation_date}" if valuation_date else f"{self.BASE_URL}/latest"
        params = {
            'access_key': self.access_key,
            'base': source_currency,
            'symbols': exchanged_currency,
        }
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rate_value = data['rates'].get(exchanged_currency)
                if rate_value:
                    return {
                        'source_currency': source_currency,
                        'exchanged_currency': exchanged_currency,
                        'rate_value': rate_value,
                        'valuation_date': valuation_date or data['date'],
                        'provider': 'Fixer'
                    }
            logging.error(f"API Error: {data.get('error')}")
        else:
            logging.error(f"Request failed with status: {response.status_code}")

        return None  # If rate not found

    def get_historical_rates(self, source_currency, exchanged_currency, start_date):
        end_date = datetime.now().date()
        rates = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            rate_data = self.get_exchange_rate(source_currency, exchanged_currency, date_str)
            if rate_data:
                rates.append(rate_data)
            else:
                logging.warning(f"No rate found for {date_str}.")
            current_date += timedelta(days=1)

        return rates

    @staticmethod
    def get_local_exchange_rate(source_code, target_code):
        """Fetches the exchange rate from the local database."""
        try:
            exchange_rate = CurrencyExchangeRate.objects.get(
                source_currency__code=source_code,
                exchanged_currency__code=target_code
            )
            return exchange_rate.rate_value
        except CurrencyExchangeRate.DoesNotExist:
            logging.warning(f"Local rate not found for {source_code}/{target_code}.")
            return None
        
    def calculate_twr(self, source_currency, exchanged_currency, amount, start_date, cash_flows):
        """Calculate Time-Weighted Return (TWR) using exchange rates from the Fixer API."""
        historical_rates = self.get_historical_rates(source_currency, exchanged_currency, start_date)
        twr_values = []
        previous_balance = amount

        # Calculate TWR based on historical rates and cash flows
        for cash_flow in cash_flows:
            flow_date = cash_flow['date']
            flow_amount = cash_flow['amount']
            rate_value = next((rate['rate_value'] for rate in historical_rates if rate['valuation_date'] <= flow_date), None)

            if rate_value is not None:
                previous_balance *= (1 + (rate_value - 1))
            
            previous_balance += flow_amount
            twr_values.append(previous_balance)

        # Final TWR calculation
        final_twr = 1
        for rate in historical_rates:
            final_twr *= (1 + (rate['rate_value'] - 1))
        final_twr -= 1

        return {'final_twr': final_twr, 'twr_values': twr_values}