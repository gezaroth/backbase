import csv
from django.core.management.base import BaseCommand
from exchange.models import CurrencyExchangeRate, Currency
from django.utils.dateparse import parse_date

# Define a dictionary mapping currency codes to their names and symbols
CURRENCY_INFO = {
    'USD': {'name': 'United States Dollar', 'symbol': '$'},
    'EUR': {'name': 'Euro', 'symbol': '€'},
    'GBP': {'name': 'British Pound Sterling', 'symbol': '£'},
    'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr'},
}

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

            # Print the fieldnames (headers) of the CSV for debugging
            print("CSV Headers:", reader.fieldnames)

            for row in reader:
                print("Row being processed:", row)  # Debugging output

                source_currency_code = row.get('source_currency', None)
                exchanged_currency_code = row.get('exchanged_currency', None)
                valuation_date_str = row.get('valuation_date', None)  # Get date as string
                rate_value = row.get('rate_value', None)

                # Check for missing data
                if not source_currency_code or not exchanged_currency_code or not valuation_date_str or rate_value is None:
                    self.stdout.write(self.style.WARNING('Skipping row due to missing data: {}'.format(row)))
                    continue  # Skip to the next iteration if any key is missing

                # Parse the date only if it is a valid string
                try:
                    valuation_date = parse_date(valuation_date_str)  # Attempt to parse the date
                    if valuation_date is None:
                        raise ValueError(f"Invalid date format: {valuation_date_str}")  # Raise an error if date parsing fails
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error parsing date for row {row}: {e}'))
                    continue  # Skip to the next iteration if date parsing fails

                # Get or create the source currency
                source_currency, _ = Currency.objects.get_or_create(
                    code=source_currency_code,
                    defaults={
                        'name': CURRENCY_INFO.get(source_currency_code, {}).get('name', 'Unknown Currency'),
                        'symbol': CURRENCY_INFO.get(source_currency_code, {}).get('symbol', '')
                    }
                )

                # Get or create the exchanged currency
                exchanged_currency, _ = Currency.objects.get_or_create(
                    code=exchanged_currency_code,
                    defaults={
                        'name': CURRENCY_INFO.get(exchanged_currency_code, {}).get('name', 'Unknown Currency'),
                        'symbol': CURRENCY_INFO.get(exchanged_currency_code, {}).get('symbol', '')
                    }
                )

                # Create the exchange rate record
                CurrencyExchangeRate.objects.create(
                    source_currency=source_currency,
                    exchanged_currency=exchanged_currency,
                    valuation_date=valuation_date,
                    rate_value=rate_value
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported exchange rates.'))
