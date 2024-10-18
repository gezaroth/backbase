import csv
from django.core.management.base import BaseCommand
from exchange.models import CurrencyExchangeRate, Currency
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Import exchange rates from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        self.import_from_csv(file_path)

    def import_from_csv(self, file_path):
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Read fields from the row
                source_currency_code = row['source_currency']
                exchanged_currency_code = row['exchanged_currency']
                valuation_date = parse_date(row['valuation_date'])
                rate_value = row['rate_value']

                # Get or create the source currency
                source_currency, _ = Currency.objects.get_or_create(code=source_currency_code)

                # Get or create the exchanged currency
                exchanged_currency, _ = Currency.objects.get_or_create(code=exchanged_currency_code)

                # Create the exchange rate record
                CurrencyExchangeRate.objects.create(
                    source_currency=source_currency,
                    exchanged_currency=exchanged_currency,
                    valuation_date=valuation_date,
                    rate_value=rate_value
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported exchange rates.'))
