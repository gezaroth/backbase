from exchange.models import Provider
from .fixer_provider import FixerProvider
from .mock_provider import MockProvider
from .local_provider import LocalExchangeRateProvider  
import logging


FIXER_API_KEY = 'd201928fea2339726ff54ceaefabeb9c'

class ProviderManager:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock  
        self.providers = self.load_providers()

    def load_providers(self):
        """Load providers in order: Fixer > Mock > Local."""
        provider_instances = []
        # Always start with FixerProvider
        provider_instances.append(FixerProvider(access_key=FIXER_API_KEY))  # Fixer API key

        if self.use_mock:
            provider_instances.append(MockProvider())
        else:
            provider_instances.append(LocalExchangeRateProvider())  # Local provider
            provider_instances.append(MockProvider())  # Add Mock at the end if not using mock

        return provider_instances

    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date=None):
        """Try each provider based on priority until one succeeds."""
        for provider in self.providers:
            try:
                rate = provider.get_exchange_rate(source_currency, exchanged_currency, valuation_date)
                if rate:
                    return rate
            except Exception as e:
                logging.error(f"Provider {provider.__class__.__name__} failed: {e}")
        raise Exception("No providers available for the requested exchange rate")

    def get_historical_rates(self, source_currency, exchanged_currency, start_date):
        """Try each provider for historical rates."""
        for provider in self.providers:
            try:
                rates = provider.get_historical_rates(source_currency, exchanged_currency, start_date)
                if rates:
                    return rates
            except Exception as e:
                logging.error(f"Provider {provider.__class__.__name__} failed: {e}")
        raise Exception("No providers available for historical rates")
    
    def calculate_twr(self, source_currency, exchanged_currency, amount, start_date, cash_flows):
        """Try to calculate TWR using each provider in priority order."""
        for provider in self.providers:
            try:
                if hasattr(provider, 'calculate_twr'):
                    twr = provider.calculate_twr(source_currency, exchanged_currency, amount, start_date, cash_flows)
                    if twr:
                        return twr
            except Exception as e:
                logging.error(f"Error with provider {provider.__class__.__name__}: {e}")
        return None
