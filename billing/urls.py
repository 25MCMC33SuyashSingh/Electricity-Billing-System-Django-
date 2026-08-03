from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin
    path('new-customer/', views.add_customer, name='add_customer'),
    path('meter-info/<int:customer_id>/', views.meter_info, name='meter_info'),
    path('calculate-bill/', views.calculate_bill, name='calculate_bill'),
    path('submit-bill/', views.submit_bill, name='submit_bill'),
    path('customers/', views.customer_list, name='customer_list'),
    path('deposits/', views.deposit_list, name='deposit_list'),

    # Customer
    path('bill-details/', views.bill_details, name='bill_details'),
    path('pay-bill/', views.pay_bill, name='pay_bill'),
    path('payment-receipt/', views.payment_receipt, name='payment_receipt'),
    path('generate-bill/', views.generate_bill, name='generate_bill'),
    path('update-info/', views.update_info, name='update_info'),
    path('view-info/', views.view_info, name='view_info'),
]
