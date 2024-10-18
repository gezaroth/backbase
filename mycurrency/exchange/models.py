# models.py

from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name='exchanges', on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, max_digits=18, decimal_places=6)

    @classmethod
    def get_exchange_rate(cls, source_code, target_code):
        try:
            rate = cls.objects.get(
                source_currency__code=source_code,
                exchanged_currency__code=target_code
            )
            return rate.rate_value
        except cls.DoesNotExist:
            return None  # or raise an exception

class Provider(models.Model):
    name = models.CharField(max_length=50, unique=True)
    priority = models.IntegerField(default=0)  
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
