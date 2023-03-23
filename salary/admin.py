from django.contrib import admin
from .models import Department, Employee, Client, Cash, Payment, StaticCost, StaticCash, Tax


# Register your models here.
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name_department']

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'post_name']

class CashAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'income', 'income_item', 'client_id']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'payment', 'employee_id']

class StaticCostAdmin(admin.ModelAdmin):
    list_display = ['cost_name', 'cost_sum', 'comment']

class StaticCashAdmin(admin.ModelAdmin):
    list_display = ['cash_name', 'cash_sum', 'comment']

class TaxAdmin(admin.ModelAdmin):
    list_display = ['tax_name', 'tax_sum', 'comment']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_name']

@admin.register(Cash)
class CashAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'income', 'client_id', 'income_item']


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(StaticCost, StaticCostAdmin)
admin.site.register(StaticCash, StaticCashAdmin)
admin.site.register(Tax, TaxAdmin)
