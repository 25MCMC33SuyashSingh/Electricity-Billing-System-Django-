from django.contrib import admin
from .models import Customer, MeterRecord, Tariff, Bill, PaymentLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'meter_no', 'city', 'state', 'email', 'phone_no')
    search_fields = ('name', 'meter_no')


@admin.register(MeterRecord)
class MeterRecordAdmin(admin.ModelAdmin):
    list_display = ('customer', 'meter_location', 'meter_type', 'phase_code', 'bill_type', 'days')


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('unit_rate', 'meter_rent', 'service_charge', 'energy_tax', 'green_cess', 'fixed_charge')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('customer', 'month', 'unit', 'total_bill', 'status', 'payment_method', 'payment_date', 'paid_amount')
    search_fields = ('customer__meter_no',)


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'customer', 'month', 'amount', 'payment_method', 'payment_date')
