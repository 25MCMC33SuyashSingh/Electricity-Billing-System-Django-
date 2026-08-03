from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    meter_no = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='Uttar Pradesh')
    email = models.EmailField(max_length=120, blank=True)
    phone_no = models.CharField(max_length=20, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer')

    def __str__(self):
        return f'{self.name} ({self.meter_no})'


class MeterRecord(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='meter')
    meter_location = models.CharField(max_length=50)
    meter_type = models.CharField(max_length=50)
    phase_code = models.CharField(max_length=30)
    bill_type = models.CharField(max_length=30)
    days = models.CharField(max_length=10, default='30')

    def __str__(self):
        return f'Meter {self.customer.meter_no}'


class Tariff(models.Model):
    unit_rate = models.IntegerField(default=8)
    meter_rent = models.IntegerField(default=60)
    service_charge = models.IntegerField(default=25)
    energy_tax = models.IntegerField(default=6)
    green_cess = models.IntegerField(default=10)
    fixed_charge = models.IntegerField(default=20)

    class Meta:
        verbose_name = 'Tariff'
        verbose_name_plural = 'Tariff Rates'

    def __str__(self):
        return f'Rate: {self.unit_rate}/unit'


class Bill(models.Model):
    STATUS_CHOICES = [('Not Paid', 'Not Paid'), ('Paid', 'Paid')]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bills')
    month = models.CharField(max_length=20)
    unit = models.CharField(max_length=20)
    total_bill = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Paid')
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    paid_amount = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ('customer', 'month')

    def __str__(self):
        return f'{self.customer.meter_no} - {self.month} - {self.total_bill}'


class PaymentLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    month = models.CharField(max_length=20)
    amount = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment #{self.pk} - {self.customer.meter_no}'
