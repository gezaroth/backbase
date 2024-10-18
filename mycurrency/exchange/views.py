import logging
import os
from dotenv import load_dotenv
from exchange.providers.local_provider import LocalExchangeRateProvider
from .providers.fixer_provider import FixerProvider
from .providers.mock_provider import MockProvider
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from exchange.providers.provider_manager import ProviderManager
from .models import Currency
from django.shortcuts import render
from rest_framework import status
from decimal import Decimal

load_dotenv()

FIXER_API_KEY = os.getenv('FIXER_API_KEY')


if not FIXER_API_KEY:
    raise ValueError("FIXER_API_KEY is not set in the environment variables")


CURRENCIES = {
    'EUR': {'name': 'Euro', 'symbol': '€'},
    'USD': {'name': 'US Dollar', 'symbol': '$'},
    'GBP': {'name': 'British Pound Sterling', 'symbol': '£'},
    'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr'},
}


@api_view(['POST'])
def get_exchange_rates_for_date_range(request):
    """
    Retrieve exchange rates between two currencies for a specified date range.
    Uses the provider manager to fall back between providers if necessary.
    """
    source_currency = request.data.get('source_currency')
    exchanged_currency = request.data.get('exchanged_currency')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    use_mock = request.data.get('use_mock', False)

    # Validate currencies
    if source_currency not in CURRENCIES or exchanged_currency not in CURRENCIES:
        return Response({'error': 'Invalid currency codes.'}, status=status.HTTP_400_BAD_REQUEST)

    # Parse and validate the date range
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    if start_date > end_date:
        return Response({'error': 'Start date must be before or equal to end date.'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize the provider manager
    provider_manager = ProviderManager(use_mock=use_mock)

    delta = end_date - start_date
    results = []

    for i in range(delta.days + 1):
        current_date = start_date + timedelta(days=i)
        formatted_date = current_date.strftime('%Y-%m-%d')

        # Retrieve the exchange rate for the current date
        try:
            rate_data = provider_manager.get_exchange_rate(source_currency, exchanged_currency, formatted_date)
            if rate_data:
                results.append({
                    'date': formatted_date,
                    'rate_value': rate_data['rate_value'],
                    'provider': rate_data['provider'],
                    'valuation_date': rate_data['valuation_date'],
                })
            else:
                results.append({
                    'date': formatted_date,
                    'rate_value': 'Data unavailable',
                    'provider': 'N/A',
                    'valuation_date': 'N/A'
                })
        except Exception as e:
            logging.error(f"Error retrieving rate for {formatted_date}: {e}")
            results.append({
                'date': formatted_date,
                'rate_value': 'Error',
                'provider': 'N/A',
                'valuation_date': 'N/A'
            })

    return Response({'exchange_rates': results}, status=status.HTTP_200_OK)


@api_view(['POST'])
def latast_exchange_rate(request):
    source_currency = request.data.get('source_currency')
    amount = request.data.get('amount')
    exchanged_currency = request.data.get('exchanged_currency')
    use_mock = request.data.get('use_mock', False)
    use_local = request.data.get('use_local', False)

    if source_currency not in CURRENCIES or exchanged_currency not in CURRENCIES:
        return Response({'error': 'Invalid currency codes.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Amount must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize the provider manager with respect to the mock usage flag
    provider_manager = ProviderManager(use_mock=use_mock)

    # Get exchange rate using the provider manager
    try:
        rates_data = provider_manager.get_exchange_rate(source_currency, exchanged_currency)
        rate_value = Decimal(rates_data['rate_value'])
        converted_amount = amount * rate_value

        return Response({
            'source_currency': source_currency,
            'amount': amount,
            'exchanged_currency': exchanged_currency,
            'converted_amount': round(converted_amount, 2),
            'rate_value': rate_value,
            'valuation_date': rates_data['valuation_date'],
            'provider': rates_data['provider']
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def calculate_twr(request):
    source_currency = request.data.get('source_currency')
    amount = request.data.get('amount')
    exchanged_currency = request.data.get('exchanged_currency')
    start_date = request.data.get('start_date')
    cash_flows = request.data.get('cash_flows', [])
    use_mock = request.data.get('use_mock', False)
    use_local = request.data.get('use_local', False)

    # Convert start_date to a datetime object
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if use_mock:
        provider = MockProvider()
    elif use_local:
        provider = LocalExchangeRateProvider()
    else:
        api_key = FIXER_API_KEY
        provider = FixerProvider(api_key)

    # Get historical rates
    historical_rates = provider.get_historical_rates(source_currency, exchanged_currency, start_date)

    # Calculate TWRR using historical rates and cash flows
    twr_values = []
    previous_balance = amount

    for cash_flow in cash_flows:
        flow_date = datetime.strptime(cash_flow['date'], '%Y-%m-%d').date()
        
        # Calculate rates up to the cash flow date
        for rate in historical_rates:
            if rate['valuation_date'] <= flow_date.strftime('%Y-%m-%d'):
                rate_value = rate['rate_value']
                # Update balance based on the rate
                previous_balance = previous_balance * (1 + (rate_value - 1))
        
        # Apply cash flow
        previous_balance += cash_flow['amount']
        # Store TWR value at this cash flow
        twr_values.append(previous_balance)

    # Calculate final TWR
    final_twr = 1
    for rate in historical_rates:
        final_twr *= (1 + (rate['rate_value'] - 1))

    final_twr -= 1  # Final TWR calculation

    return Response({'final_twr': final_twr, 'twr_values': twr_values}, status=status.HTTP_200_OK)




def currency_converter_view(request):
    currencies = Currency.objects.all()
    return render(request, 'admin/currency_converter.html', {'currencies': currencies})


def graph_view(request):
    rates1 = []
    rates2 = []
    labels = []
    currency1 = currency2 = None

    if request.method == 'POST':
        currency1 = request.POST.get('currency1')
        currency2 = request.POST.get('currency2')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parse the start and end dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        provider_manager = ProviderManager()

        try:
            # Get historical rates for both currencies
            historical_rates1 = provider_manager.get_historical_rates(currency1, currency2, start_date)
            historical_rates2 = provider_manager.get_historical_rates(currency2, currency1, start_date)

            # Collect rates and labels
            for rate in historical_rates1:
                labels.append(rate['valuation_date'])
                rates1.append(rate['rate_value'])

            for rate in historical_rates2:
                rates2.append(rate['rate_value'])

            # Debugging information
            print(f"Labels: {labels}")
            print(f"Rates1: {rates1}")
            print(f"Rates2: {rates2}")

        except Exception as e:
            logging.error(f"Error fetching exchange rates: {e}")

    return render(request, 'admin/exchange_rate_graph.html', {
        'currency1': currency1,
        'currency2': currency2,
        'labels': labels,
        'rates1': rates1,
        'rates2': rates2,
    })
