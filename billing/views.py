from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import Bill, Customer, MeterRecord, PaymentLog, Tariff

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

COMPANY = {
    'name': 'UPPCL - Uttar Pradesh Power Corporation Limited',
    'division': 'Lucknow Power Distribution Division',
    'address': 'Shakti Bhawan, Gomti Nagar, Lucknow, Uttar Pradesh - 226010',
    'helpline': '1912',
    'email': 'support@uppcl.co.in',
}

is_admin = user_passes_test(lambda u: u.is_staff)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid login details.')
    return render(request, 'billing/login.html', {'company': COMPANY})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        meter_no = request.POST.get('meter_no')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        try:
            customer = Customer.objects.get(meter_no=meter_no)
        except Customer.DoesNotExist:
            messages.error(request, 'No customer found for this meter number.')
            return render(request, 'billing/register.html', {'company': COMPANY})
        if customer.user is not None:
            messages.error(request, 'This meter number is already registered.')
            return render(request, 'billing/register.html', {'company': COMPANY})
        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'billing/register.html', {'company': COMPANY})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'billing/register.html', {'company': COMPANY})
        user = User.objects.create_user(username=username, password=password)
        customer.user = user
        customer.name = name
        customer.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'billing/register.html', {'company': COMPANY})


def logout_view(request):
    logout(request)
    return redirect('login')


def _customer_of(user):
    try:
        return user.customer
    except Customer.DoesNotExist:
        return None


@login_required
def dashboard(request):
    if request.user.is_staff:
        context = {
            'company': COMPANY,
            'customers': Customer.objects.count(),
            'bills': Bill.objects.count(),
            'paid': Bill.objects.filter(status='Paid').count(),
            'unpaid': Bill.objects.filter(status='Not Paid').count(),
            'payments': PaymentLog.objects.count(),
        }
        return render(request, 'billing/admin_dashboard.html', context)
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    context = {
        'company': COMPANY,
        'customer': customer,
        'bills': Bill.objects.filter(customer=customer),
        'unpaid_count': Bill.objects.filter(customer=customer, status='Not Paid').count(),
    }
    return render(request, 'billing/customer_dashboard.html', context)


# ------------------------- ADMIN -------------------------

@is_admin
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state') or 'Uttar Pradesh'
        email = request.POST.get('email')
        phone = request.POST.get('phone_no')
        meter_no = _generate_meter_no()
        customer = Customer.objects.create(
            name=name, meter_no=meter_no, address=address, city=city,
            state=state, email=email, phone_no=phone)
        messages.success(request, f'Customer added. Meter number: {meter_no}')
        return redirect('meter_info', customer.pk)
    return render(request, 'billing/add_customer.html', {'company': COMPANY})


@is_admin
def meter_info(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        MeterRecord.objects.update_or_create(
            customer=customer,
            defaults={
                'meter_location': request.POST.get('meter_location'),
                'meter_type': request.POST.get('meter_type'),
                'phase_code': request.POST.get('phase_code'),
                'bill_type': request.POST.get('bill_type'),
                'days': request.POST.get('days', '30'),
            })
        messages.success(request, 'Meter information saved successfully.')
        return redirect('dashboard')
    return render(request, 'billing/meter_info.html',
                  {'company': COMPANY, 'customer': customer, 'months': MONTHS})


@is_admin
def calculate_bill(request):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=request.POST.get('customer_id'))
        month = request.POST.get('month')
        try:
            units = int(request.POST.get('unit'))
        except (TypeError, ValueError):
            messages.error(request, 'Please enter valid units.')
            return redirect('calculate_bill')
        if Bill.objects.filter(customer=customer, month=month).exists():
            messages.error(request, f'Bill already generated for {month}.')
            return redirect('calculate_bill')
        tariff = _get_tariff()
        total = units * tariff.unit_rate + tariff.meter_rent + tariff.service_charge \
            + tariff.energy_tax + tariff.green_cess + tariff.fixed_charge
        Bill.objects.create(customer=customer, month=month, unit=str(units),
                            total_bill=str(total), status='Not Paid')
        messages.success(request, f'Bill of Rs. {total} generated for {customer.meter_no}.')
        return redirect('calculate_bill')
    context = {'company': COMPANY, 'customers': Customer.objects.all(), 'months': MONTHS}
    return render(request, 'billing/calculate_bill.html', context)


@is_admin
def submit_bill(request):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=request.POST.get('customer_id'))
        month = request.POST.get('month')
        method = request.POST.get('method', 'Cash')
        bill = Bill.objects.filter(customer=customer, month=month).first()
        if bill is None:
            messages.error(request, 'No bill found for this meter and month.')
            return redirect('submit_bill')
        bill.status = 'Paid'
        bill.payment_method = method
        bill.payment_date = _now()
        bill.paid_amount = bill.total_bill
        bill.save()
        PaymentLog.objects.create(customer=customer, month=month,
                                  amount=bill.total_bill, payment_method=method)
        messages.success(request, f'Payment of Rs. {bill.total_bill} recorded ({method}).')
        return redirect('submit_bill')
    context = {'company': COMPANY, 'customers': Customer.objects.all(), 'months': MONTHS}
    return render(request, 'billing/submit_bill.html', context)


@is_admin
def customer_list(request):
    customers = Customer.objects.all()
    meter = request.GET.get('meter', '')
    name = request.GET.get('name', '')
    if meter:
        customers = customers.filter(meter_no=meter)
    if name:
        customers = customers.filter(name__icontains=name)
    return render(request, 'billing/customer_list.html',
                  {'company': COMPANY, 'customers': customers, 'meter': meter, 'name': name})


@is_admin
def deposit_list(request):
    bills = Bill.objects.select_related('customer').all()
    meter = request.GET.get('meter', '')
    month = request.GET.get('month', '')
    if meter:
        bills = bills.filter(customer__meter_no=meter)
    if month:
        bills = bills.filter(month=month)
    return render(request, 'billing/deposit_list.html',
                  {'company': COMPANY, 'bills': bills, 'meter': meter, 'month': month, 'months': MONTHS})


# ------------------------- CUSTOMER -------------------------

@login_required
def bill_details(request):
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    return render(request, 'billing/bill_details.html', {
        'company': COMPANY,
        'customer': customer,
        'bills': Bill.objects.filter(customer=customer).order_by('month'),
        'payments': PaymentLog.objects.filter(customer=customer).order_by('-payment_date'),
    })


@login_required
def pay_bill(request):
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    selected = None
    month = request.POST.get('month')
    if request.method == 'POST':
        bill = Bill.objects.filter(customer=customer, month=month).first()
        if bill is None:
            messages.error(request, 'No bill found for this month.')
        elif bill.status == 'Paid':
            messages.warning(request, 'This bill has already been paid.')
        else:
            bill.status = 'Paid'
            bill.payment_method = 'Online'
            bill.payment_date = _now()
            bill.paid_amount = bill.total_bill
            bill.save()
            PaymentLog.objects.create(customer=customer, month=month,
                                      amount=bill.total_bill, payment_method='Online')
            messages.success(request, f'Payment of Rs. {bill.total_bill} successful!')
            return redirect('payment_receipt')
        return redirect('pay_bill')
    month = request.GET.get('month')
    if month:
        selected = Bill.objects.filter(customer=customer, month=month).first()
    return render(request, 'billing/pay_bill.html', {
        'company': COMPANY, 'customer': customer, 'months': MONTHS, 'selected': selected, 'month': month,
    })


@login_required
def payment_receipt(request):
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    last = PaymentLog.objects.filter(customer=customer).order_by('-payment_date').first()
    return render(request, 'billing/payment_receipt.html', {
        'company': COMPANY, 'customer': customer, 'payment': last,
    })


@login_required
def generate_bill(request):
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    month = request.GET.get('month')
    bill = None
    if month:
        bill = Bill.objects.filter(customer=customer, month=month).first()
    return render(request, 'billing/generate_bill.html', {
        'company': COMPANY, 'customer': customer, 'months': MONTHS,
        'bill': bill, 'month': month,
        'meter': getattr(customer, 'meter', None),
        'tariff': _get_tariff(),
    })


@login_required
def update_info(request):
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.address = request.POST.get('address')
        customer.city = request.POST.get('city')
        customer.state = request.POST.get('state')
        customer.email = request.POST.get('email')
        customer.phone_no = request.POST.get('phone_no')
        customer.save()
        messages.success(request, 'Information updated successfully.')
        return redirect('view_info')
    return render(request, 'billing/update_info.html', {'company': COMPANY, 'customer': customer})


@login_required
def view_info(request):
    customer = _customer_of(request.user)
    if customer is None:
        return render(request, 'billing/no_profile.html', {'company': COMPANY})
    return render(request, 'billing/view_info.html', {'company': COMPANY, 'customer': customer})


# ------------------------- HELPERS -------------------------

def _generate_meter_no():
    import random
    while True:
        meter = 'UP' + str(random.randint(1000000, 9999999))
        if not Customer.objects.filter(meter_no=meter).exists():
            return meter


def _get_tariff():
    tariff, _ = Tariff.objects.get_or_create(pk=1)
    return tariff


def _now():
    from django.utils import timezone
    return timezone.now()
