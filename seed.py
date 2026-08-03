"""Seed script: creates admin + sample customers + bills.

Run with:  python manage.py shell < seed.py
"""
from datetime import datetime
from django.contrib.auth.models import User
from billing.models import Customer, MeterRecord, Tariff, Bill, PaymentLog

def ensure_tariff():
    t, _ = Tariff.objects.get_or_create(pk=1)
    t.unit_rate = 8
    t.meter_rent = 60
    t.service_charge = 25
    t.energy_tax = 6
    t.green_cess = 10
    t.fixed_charge = 20
    t.save()
    return t

def make_customer(name, meter, city, phone, email, user=None):
    return Customer.objects.get_or_create(
        meter_no=meter,
        defaults={'name': name, 'address': f'House {city}', 'city': city,
                  'state': 'Uttar Pradesh', 'email': email, 'phone_no': phone, 'user': user})[0]

def make_meter(customer, mtype='Single-Phase', phase='011 - Lucknow',
               bill_type='Domestic', location='Inside Premises'):
    MeterRecord.objects.get_or_create(
        customer=customer,
        defaults={'meter_location': location, 'meter_type': mtype,
                  'phase_code': phase, 'bill_type': bill_type, 'days': '30'})

def make_bill(customer, month, units, tariff, status='Not Paid', method=None, paid_at=None):
    total = units * tariff.unit_rate + tariff.meter_rent + tariff.service_charge \
        + tariff.energy_tax + tariff.green_cess + tariff.fixed_charge
    bill, created = Bill.objects.get_or_create(
        customer=customer, month=month,
        defaults={'unit': str(units), 'total_bill': str(total), 'status': 'Not Paid'})
    if status == 'Paid' and method and paid_at:
        bill.status = 'Paid'
        bill.payment_method = method
        bill.payment_date = paid_at
        bill.paid_amount = str(total)
        bill.save()
        PaymentLog.objects.get_or_create(
            customer=customer, month=month, amount=str(total),
            defaults={'payment_method': method, 'payment_date': paid_at})
    return bill

# Admin
admin_user, created = User.objects.get_or_create(username='uppcladmin')
if created:
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.first_name = 'UPPCL'
    admin_user.last_name = 'Administrator'
    admin_user.save()
    print('Admin created: uppcladmin / admin123')

tariff = ensure_tariff()

# Customers with login accounts
data = [
    ('Suyash Singh', 'UP6748321', 'Varanasi', '9845678903', 'suyash.singh@gmail.com', 'suyash.singh', 'suyash@123', 'Single-Phase', '044 - Varanasi', 'Domestic'),
    ('Shivam Singh', 'UP4521301', 'Lucknow', '9812345670', 'shivam.singh@gmail.com', 'shivam.singh', 'shivam@123', 'Single-Phase', '011 - Lucknow', 'Domestic'),
    ('Aman Chaudhary', 'UP5102347', 'Ambedkarnagar', '9865712390', 'aman.chaudhary@gmail.com', 'aman.chaudhary', 'aman@123', 'Three-Phase', '077 - Prayagraj', 'Commercial'),
    ('Ashish', 'UP7220458', 'Kanpur', '9823456781', 'ashish.k@gmail.com', 'ashish', 'ashish@123', 'Smart Meter', '022 - Kanpur', 'Domestic'),
    ('Ajit Tiwari', 'UP3189756', 'Gorakhpur', '9856789014', 'ajit.tiwari@gmail.com', 'ajit.tiwari', 'ajit@123', 'Three-Phase', '055 - Gorakhpur', 'Industrial'),
]

for name, meter, city, phone, email, uname, pwd, mtype, phase, btype in data:
    user, created = User.objects.get_or_create(username=uname)
    if created:
        user.set_password(pwd)
        user.save()
    cust = make_customer(name, meter, city, phone, email, user)
    make_meter(cust, mtype, phase, btype)
    print(f'Customer ready: {name} / {meter} -> {uname} / {pwd}')

# Bills: July paid + August unpaid
months = [('July', 'Paid'), ('August', 'Not Paid')]
units_map = {'UP6748321': (95, 105), 'UP4521301': (110, 125), 'UP5102347': (260, 305),
             'UP7220458': (95, 140), 'UP3189756': (480, 510)}
from django.utils import timezone
for meter, (july_units, aug_units) in units_map.items():
    cust = Customer.objects.get(meter_no=meter)
    make_bill(cust, 'July', july_units, tariff, 'Paid', 'Cash' if meter in ('UP4521301', 'UP3189756') else 'Online',
              paid_at=timezone.make_aware(datetime(2026, 7, 10, 10, 30)))
    make_bill(cust, 'August', aug_units, tariff)

print('SEED COMPLETE')
