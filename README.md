# MyCurrency API Documentation

## Overview

MyCurrency is a RESTful API built with Python and Django designed to provide currency exchange rates using multiple data providers. The primary goal of MyCurrency is to retrieve and store daily currency rates while offering flexibility to incorporate various currency data providers. 

### Key Features
- **Multi-Provider Support**: Utilizes an external provider (Fixer.io) and supports local and mock providers.
- **Resilient-Provider / Fall-Back Re-try**: If one of the providers “fails” or get no rates, the platform has to try with the next one in order of priority.
- **Core Functions**:
  - Retrieve exchange rates between two currencies for a specified period.
  - Calculate the latest exchange rate between two currencies.
  - Retrieve Time-Weighted Rate (TWR) for investment analysis.
### Providers
1. **Fixer.io**: 
   - An external API provider that supplies current and historical currency rates. 
   - Requires an API key for access.

2. **Local Provider**: 
   - Utilizes a CSV file containing currency exchange ratios for various accepted currencies and dates.

3. **Mock Provider**: 
   - Generates random exchange rates for testing purposes when data is not available in the Local Provider or from Fixer.io.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/MyCurrency.git
   cd MyCurrency
   ```

2. **Install requirements**:
   Ensure you have Python and pip installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**:
   Create a `.env` file in the root directory and add your Fixer.io API key:
   ```env
   FIXER_API_KEY='your_fixer_api_key'
   ```

4. **Run migrations**:
   Initialize the database:
   ```bash
   python manage.py migrate
   ```

5. **Load local data (optional)**:
   If you have a CSV file for the Local Provider, load it using:
   ```bash
   python manage.py loaddata your_data_file.csv
   ```

6. **Run the server**:
   Start the Django development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### 1. Retrieve Exchange Rates
- **Endpoint**: `get-exchange-rates/`
- **Method**: `POST`
- **Request Body**:
  ```json
    {
        "source_currency": "USD",
        "exchanged_currency": "EUR",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10"
    }
  ```
- **Response**:
  ```json
    {
        "exchange_rates": [
            {
                "date": "2023-01-01",
                "rate_value": 1.406341,
                "provider": "MockProvider",
                "valuation_date": "2023-01-01"
            },
            {
                "date": "2023-01-02",
                "rate_value": 0.85158,
                "provider": "MockProvider",
                "valuation_date": "2023-01-02"
            },
            {
                "date": "2023-01-03",
                "rate_value": 0.770289,
                "provider": "MockProvider",
                "valuation_date": "2023-01-03"
            },
            {
                "date": "2023-01-04",
                "rate_value": 0.598401,
                "provider": "MockProvider",
                "valuation_date": "2023-01-04"
            },
            {
                "date": "2023-01-05",
                "rate_value": 1.282644,
                "provider": "MockProvider",
                "valuation_date": "2023-01-05"
            },
            {
                "date": "2023-01-06",
                "rate_value": 0.673991,
                "provider": "MockProvider",
                "valuation_date": "2023-01-06"
            },
            {
                "date": "2023-01-07",
                "rate_value": 0.535504,
                "provider": "MockProvider",
                "valuation_date": "2023-01-07"
            },
            {
                "date": "2023-01-08",
                "rate_value": 0.792585,
                "provider": "MockProvider",
                "valuation_date": "2023-01-08"
            },
            {
                "date": "2023-01-09",
                "rate_value": 1.281544,
                "provider": "MockProvider",
                "valuation_date": "2023-01-09"
            },
            {
                "date": "2023-01-10",
                "rate_value": 1.2889,
                "provider": "MockProvider",
                "valuation_date": "2023-01-10"
            }
        ]
    }
  ```

### 2. Calculate Latest Exchange Rate Conversion
- **Endpoint**: `api/convert/`
- **Method**: `POST`
- **Request Body**:
  ```json
    {
    "source_currency": "EUR",
    "amount": 100,
    "exchanged_currency": "USD"
    }
  ```
- **Response**:
  ```json
    {
        "source_currency": "EUR",
        "amount": 100.0,
        "exchanged_currency": "USD",
        "converted_amount": 118.0,
        "rate_value": 1.18,
        "valuation_date": "2024-10-01",
        "provider": "LocalProvider"
    }
  ```

### 3. Calculate Time-Weighted Rate (TWR)
- **Endpoint**: `/api/get-twr/`
- **Method**: `POST`
- **Request Body**:
  ```json
    {
    "source_currency": "EUR",
    "amount": 1000,
    "exchanged_currency": "USD",
    "start_date": "2024-10-06",
    "cash_flows": [
        {
        "date": "2024-10-07",
        "amount": 500
        },
        {
        "date": "2024-10-10",
        "amount": 300
        }
    ]
    }
  ```
- **Response**:
  ```json
    {
        "final_twr": 0,
        "twr_values": [
            1500,
            1800
        ]
    }
  ```

## Admin Features

### Converter View
- Provides an online currency converter where users can set a source currency and multiple target currencies to view their exchange rates and the result of the desired amount to exchange as example.



### Graph View
- Displays a graphical representation of exchange rate evolution over time, allowing users to compare different currencies visually.

## Error Handling
- The API responds with appropriate HTTP status codes and error messages for invalid requests.
- Common error codes:
  - `400 Bad Request`: Invalid input parameters.
  - `404 Not Found`: Requested resource does not exist.
  - `500 Internal Server Error`: Server-side error.

## Conclusion
The MyCurrency API provides a robust and flexible solution for retrieving and calculating currency exchange rates. With support for multiple providers and detailed functionalities, it serves as a comprehensive platform for currency-related tasks.

For further inquiries or issues, please contact the development team at gezaroth96@gmail.com.
