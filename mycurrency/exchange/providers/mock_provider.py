import random
import logging
from datetime import datetime, timedelta
from .base_provider import BaseProvider
from exchange.models import CurrencyExchangeRate
import random
import logging
from datetime import datetime, timedelta
from .base_provider import BaseProvider

class MockProvider(BaseProvider):

    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date=None):
        """Generates a random exchange rate for testing purposes."""
        rate_value = round(random.uniform(0.5, 1.5), 6)
        return {
            'source_currency': source_currency,
            'exchanged_currency': exchanged_currency,
            'rate_value': rate_value,
            'valuation_date': valuation_date or datetime.now().date(),
            'provider': 'MockProvider'
        }

    def get_historical_rates(self, source_currency, exchanged_currency, start_date):
        """Generates historical rates for testing purposes."""
        end_date = datetime.now().date()
        rates = []
        current_date = start_date

        while current_date <= end_date:
            rate_value = round(random.uniform(0.5, 1.5), 6)
            rates.append({
                'source_currency': source_currency,
                'exchanged_currency': exchanged_currency,
                'rate_value': rate_value,
                'valuation_date': current_date.strftime('%Y-%m-%d'),
                'provider': 'MockProvider'
            })
            current_date += timedelta(days=1)

        logging.info(f"MockProvider: Historical rates for {source_currency}/{exchanged_currency} from {start_date} to {end_date} -> {rates}")
        return rates

    def calculate_twr(self, source_currency, exchanged_currency, amount, start_date, cash_flows):
        """Calculate Time-Weighted Return (TWR) for mock data."""
        twr_values = []
        previous_balance = amount
        historical_rates = self.get_historical_rates(source_currency, exchanged_currency, start_date)

        for cash_flow in cash_flows:
            flow_date = datetime.strptime(cash_flow['date'], '%Y-%m-%d').date()
            for rate in historical_rates:
                if rate['valuation_date'] <= flow_date.strftime('%Y-%m-%d'):
                    previous_balance *= (1 + (rate['rate_value'] - 1))
            previous_balance += cash_flow['amount']
            twr_values.append(previous_balance)

        final_twr = 1
        for rate in historical_rates:
            final_twr *= (1 + (rate['rate_value'] - 1))
        final_twr -= 1

        return final_twr

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
