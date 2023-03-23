from django.urls import path
from .views import main_menu, OneCLient, AllEmployees, AllCLients, \
    OneEmployee, AllCash, UpdateFormClient, CreateFormClient, CreateFormEmployee, UpdateFormEmployee, \
    UpdateFormCash, CreateFormCash, UpdateFormPayEmployee, CreateFormPayEmployee, AllPayments, OneCash, \
    change_status, Calendar, RegisterUser, LoginUser, logout_user, AddStaticCash, AddStaticCost, AddTax, refresh_cash

urlpatterns = [
    path('', LoginUser.as_view(), ),
    path('main', main_menu, name='main_menu' ),
    path('clients', AllCLients.as_view(), name='all_clients'),
    path('clients/<int:id_client>', OneCLient.as_view(),  name='client_detail'),
    path('employees/<int:id_employee>', OneEmployee.as_view(),  name='employee_detail'),
    path('cash/<int:id_cash>', OneCash.as_view(), name='cash_detail'),
    path('employees', AllEmployees.as_view(), name='all_employees'),
    path('cash', AllCash.as_view(), name='all_cash'),
    path('payment_calendar', Calendar.as_view(), name='payment_calendar'),
    path('add_static_cost/<int:pk>', AddStaticCost.as_view(), name='add_static_cost'),
    path('add_static_cash/<int:pk>', AddStaticCash.as_view(), name='add_static_cash'),
    path('add_tax/<int:pk>', AddTax.as_view(), name='add_tax'),
    path('payments', AllPayments.as_view(), name='all_payments'),
    path('update/<int:pk>', UpdateFormClient.as_view(), name='update_client'),
    path('add_client', CreateFormClient.as_view(), name='add_client'),
    path('add_employee', CreateFormEmployee.as_view(), name='add_employee'),
    path('add_payment', CreateFormPayEmployee.as_view(), name='add_payment'),
    path('edit_employee/<int:pk>', UpdateFormEmployee.as_view(), name='update_employee'),
    path('add_cash', CreateFormCash.as_view(), name='add_cash'),
    path('edit_cash/<int:pk>', UpdateFormCash.as_view(), name='update_cash'),
    path('edit_payment/<int:pk>', UpdateFormPayEmployee.as_view(), name='update_payment'),
    path('edit_status/<int:id_payment>', change_status, name='change_status'),
    path('register_user', RegisterUser.as_view(), name='register_user'),
    path('login', LoginUser.as_view(), name='login_user'),
    path('logout', logout_user, name='logout'),
    path('refresh_cash', refresh_cash, name='refresh_cash'),
]