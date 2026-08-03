# Electricity Billing System (Django)

A web-based **Electricity Billing System** for **Uttar Pradesh Power Corporation Limited (UPPCL)**, built with Django. It lets an admin manage customers, meters, tariffs and bills, while registered customers can view their bill details, generate bills, pay online and update their profile.

Originally a Java Swing desktop application, this version reimplements the full system as a modern web app.

## Features

### Admin
- Register new customers and their meter information
- Calculate and submit monthly bills (tariff-aware with energy tax, green cess, meter rent, service & fixed charges)
- View all customer details and deposit/payment history
- Django admin panel at `/admin/`

### Customer
- Self-registration by entering an existing meter number
- View bill details and payment history
- Pay bills online and download a printable payment receipt
- Generate a bill for any month
- Update and view personal information

## Tech Stack

- **Django 6.0** (Python 3.14)
- **SQLite** database (default)
- Bootstrap-free custom green UPPCL-themed UI
- Server-rendered templates with Django auth

## Getting Started

### Prerequisites
- Python 3.14+
- `pip install django`

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/25MCMC33SuyashSingh/Electricity-Billing-System-Django-.git
cd Electricity-Billing-System-Django-

# 2. Install dependencies
pip install django

# 3. Run migrations
python manage.py migrate

# 4. (Optional) Seed demo data - admin + 5 customers + bills
python manage.py shell < seed.py

# 5. Start the development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Demo Logins

| Role     | Username        | Password    |
|----------|-----------------|-------------|
| Admin    | `uppcladmin`    | `admin123`  |
| Customer | `suyash.singh`  | `suyash@123`|
| Customer | `shivam.singh`  | `shivam@123`|
| Customer | `aman.chaudhary`| `aman@123`  |
| Customer | `ashish`        | `ashish@123`|
| Customer | `ajit.tiwari`   | `ajit@123`  |

## Project Structure

```
billing_project/        # Django project settings
billing/                # Main app
  ├── models.py         # Customer, MeterRecord, Tariff, Bill, PaymentLog
  ├── views.py          # All admin & customer views
  ├── urls.py           # URL routes
  ├── admin.py          # Django admin registration
  └── templates/billing/  # HTML templates
seed.py                 # Seeds demo data (admin + customers + bills)
manage.py               # Django management script
```

## URLs

| URL                 | Description                        |
|---------------------|------------------------------------|
| `/`                 | Login page                         |
| `/register/`        | Customer registration              |
| `/dashboard/`       | Role-based dashboard               |
| `/admin/`           | Django admin panel                 |
| `/new-customer/`    | Admin: add customer                |
| `/meter-info/<id>/` | Admin: add meter for a customer    |
| `/calculate-bill/`  | Admin: calculate bill              |
| `/submit-bill/`     | Admin: submit bill                 |
| `/customers/`       | Admin: customer list               |
| `/deposits/`        | Admin: deposit details             |
| `/bill-details/`    | Customer: bill details             |
| `/pay-bill/`        | Customer: pay bill                 |
| `/payment-receipt/` | Customer: payment receipt          |
| `/generate-bill/`   | Customer: generate bill            |
| `/update-info/`     | Customer: update info              |
| `/view-info/`       | Customer: view info                |

## License

For academic/educational use. Project for a MCA semester coursework.
