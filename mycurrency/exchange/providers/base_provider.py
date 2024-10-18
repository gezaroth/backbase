from abc import ABC, abstractmethod

class BaseProvider(ABC):

    @abstractmethod
    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date):
        """Method to get the exchange rate."""
        pass

    @abstractmethod
    def get_historical_rates(self, source_currency, exchanged_currency, start_date):
        """Method to get historical exchange rates."""
        pass

    @abstractmethod
    def calculate_twr(self, source_currency, exchanged_currency, amount, start_date, cash_flows):
        """Method to calculate TWR (Time-Weighted Return)."""
        pass
