from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, reverse
from .models import (
    Client,
    Employee,
    Cash,
    Payment,
    StaticCost,
    StaticCash,
    Tax,
    Department,
)
from .forms import (
    AddEmployee,
    AddCash,
    AddClient,
    AddPayment,
    AccountsListForm,
    MarketersListForm,
    EditStatusClient,
    SalesListForm,
    RegistrationUserForm,
)
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.edit import UpdateView, CreateView
from .filters import CashFilter, PaymentFilter
import datetime, calendar
import plotly.express as px
import pandas as pd
from django.core.paginator import Paginator
import requests


def main_menu(request):
    """Строит дашборд на главной"""
    all_cash = Cash.objects.order_by("-date_time")
    all_payments = Payment.objects.order_by("-date_time").filter(status="Оплачено")
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    num_days = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
    df_days = pd.DataFrame({"date": days})
    date_cash = [cash.date_time for cash in all_cash]
    date_payment = [payment.date_time for payment in all_payments]
    income = [cash.income for cash in all_cash]
    payments = [payment.payment for payment in all_payments]
    df_cash = pd.DataFrame({"date": date_cash, "income": income})
    df_payments = pd.DataFrame({"date": date_payment, "payments": payments})
    data = df_days.merge(df_cash, on="date", how="left")
    data = data.merge(df_payments, on="date", how="left")
    df_pivot = data.pivot_table(
        index="date", values=["income", "payments"], aggfunc="sum"
    ).reset_index()
    df_pivot["revenue_cum"] = df_pivot["income"].cumsum()
    df_pivot["payment_cum"] = df_pivot["payments"].cumsum()
    fig = px.line(
        df_pivot,
        x="date",
        y=["revenue_cum", "payment_cum"],
        title="Доходы и расходы по дням",
    )
    chart = fig.to_html()

    clients_working = len(
        Client.objects.filter(is_still_client__in=["Работаем", "Непонятно"])
    )

    context = {
        "chart": chart,
        "clients_working": clients_working,
    }
    return render(request, "salary/main.html", context=context)


class AllCLients(View):
    """Показывает страницу со всеми клиентами"""

    def get(self, request):
        form = AddClient()
        clients = Client.objects.order_by("client_name")
        paginator = Paginator(clients, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "page_obj": page_obj,
            "form": form,
        }
        return render(request, "salary/all_clients.html", context=context)

    def post(self, request):
        form = AddClient(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/clients")


class OneCLient(View):
    """Показывает страницу с детализацией клиента"""

    def get(self, request, id_client):
        form = EditStatusClient()
        client = get_object_or_404(Client, id=id_client)
        context = {
            "client": client,
            "form": form,
        }
        return render(request, "salary/one_client.html", context=context)

    def post(self, request, id_client):
        client_instance = Client.objects.get(pk=id_client)
        form = EditStatusClient(request.POST, instance=client_instance)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect("/clients")


class OneEmployee(View):
    """Показывает страницу с детализацией сотрудника"""

    def get(self, request, id_employee):
        form = AddPayment()
        payments = Payment.objects.filter(employee_id=id_employee)
        payment_filter = PaymentFilter(request.GET, queryset=payments)
        filtered_qs = PaymentFilter(
            request.GET, queryset=payments.order_by("-date_time")
        ).qs
        paginator = Paginator(filtered_qs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        employee = get_object_or_404(Employee, id=id_employee)

        context = {
            "employee": employee,
            "payments": payments,
            "form": form,
            "payment_filter": payment_filter,
            "page_obj": page_obj,
        }
        return render(request, "salary/one_employee.html", context=context)


def change_status(request, id_payment):
    """Меняет статус платежа на Оплачено"""
    payment = get_object_or_404(Payment, id=id_payment)
    id_employee = payment.employee_id.pk
    payment.status = "Оплачено"
    payment.save()
    return HttpResponseRedirect(reverse("employee_detail", args=(id_employee,)))


class OneCash(View):
    """Показывает страницу с детализацией платежа"""

    def get(self, request, id_cash):
        form_list_accounts = AccountsListForm()
        form_list_marketers = MarketersListForm()
        form_list_sales = SalesListForm()
        cash = get_object_or_404(Cash, id=id_cash)
        context = {
            "cash": cash,
            "form_list_accounts": form_list_accounts,
            "form_list_marketers": form_list_marketers,
            "form_list_sales": form_list_sales,
        }
        return render(request, "salary/one_cash.html", context=context)

    def post(self, request, id_cash):
        form_list_accounts = AccountsListForm(request.POST)
        form_list_marketers = MarketersListForm(request.POST)
        form_list_sales = SalesListForm(request.POST)

        motivation = {
            "account": {"junior": 0.13, "middle": 0.16, "senior": 0.2},
            "marketer": {
                "old": {"junior": 0.12, "middle": 0.23},
                "new": {"junior": 0.12, "middle": 0.23},
            },
            "sales": {"new": 0.141},
            "rom": 0.075,
            "roa": 0.075,
        }

        if Cash.objects.filter(pk=id_cash)[0].income_item == "--КУ Стартап--":
            if form_list_accounts.is_valid():
                employee_id_account = form_list_accounts.cleaned_data["account_manager"]
                if (
                    Employee.objects.filter(pk=int(employee_id_account))[0].post_name
                    == "Аккаунт-менеджер (junior)"
                ):
                    payment = (
                        Cash.objects.filter(pk=id_cash)[0].income
                        * motivation["account"]["junior"]
                    )
                    Payment.objects.create(
                        date_time=datetime.date.today(),
                        employee_id=Employee.objects.filter(pk=employee_id_account)[0],
                        payment=payment,
                        comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation['account']['junior']}",
                    )

                elif (
                    Employee.objects.filter(pk=int(employee_id_account))[0].post_name
                    == "Аккаунт-менеджер (middle)"
                ):
                    payment = (
                        Cash.objects.filter(pk=id_cash)[0].income
                        * motivation["account"]["middle"]
                    )
                    Payment.objects.create(
                        date_time=datetime.date.today(),
                        employee_id=Employee.objects.filter(pk=employee_id_account)[0],
                        payment=payment,
                        comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation['account']['middle']}",
                    )

                elif (
                    Employee.objects.filter(pk=int(employee_id_account))[0].post_name
                    == "Аккаунт-менеджер (senior)"
                ):
                    payment = (
                        Cash.objects.filter(pk=id_cash)[0].income
                        * motivation["account"]["senior"]
                    )
                    Payment.objects.create(
                        date_time=datetime.date.today(),
                        employee_id=Employee.objects.filter(pk=employee_id_account)[0],
                        payment=payment,
                        comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation['account']['senior']}",
                    )

            if form_list_marketers.is_valid():
                employee_id_marketer = form_list_marketers.cleaned_data[
                    "marketer_manager"
                ]
                if (
                    Employee.objects.filter(pk=int(employee_id_marketer))[0].post_name
                    == "Младший маркетолог"
                ):
                    if (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Старая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation["marketer"]["old"]["junior"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                        k = {motivation['marketer']['old']['junior']}",
                        )
                    elif (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Новая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation["marketer"]["new"]["junior"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                        k = {motivation['marketer']['new']['junior']}",
                        )

                elif (
                    Employee.objects.filter(pk=int(employee_id_marketer))[0].post_name
                    == "Интернет-маркетолог"
                ):
                    if (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Старая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation["marketer"]["old"]["middle"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                    k = {motivation['marketer']['old']['middle']}",
                        )
                    elif (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Новая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation["marketer"]["new"]["middle"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                    k = {motivation['marketer']['new']['middle']}",
                        )
            if form_list_sales.is_valid():
                employee_id_sales = form_list_sales.cleaned_data["sales_manager"]
                payment = (
                    Cash.objects.filter(pk=id_cash)[0].income
                    * motivation["sales"]["new"]
                )
                Payment.objects.create(
                    date_time=datetime.date.today(),
                    employee_id=Employee.objects.filter(pk=int(employee_id_sales))[0],
                    payment=payment,
                    comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                    k = {motivation['sales']['new']}",
                )
            # Платеж РОМу
            payment_rom = Cash.objects.filter(pk=id_cash)[0].income * motivation["rom"]
            Payment.objects.create(
                date_time=datetime.date.today(),
                employee_id=Employee.objects.filter(post_name="РОМ")[0],
                payment=payment_rom,
                comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation['rom']}",
            )
            # Платеж РОА
            payment_roa = Cash.objects.filter(pk=id_cash)[0].income * motivation["roa"]
            Payment.objects.create(
                date_time=datetime.date.today(),
                employee_id=Employee.objects.filter(post_name="РОА")[0],
                payment=payment_roa,
                comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation['roa']}",
            )
            status = get_object_or_404(Cash, id=id_cash)
            status.status = "Оплачено сотрудникам"
            status.save()

        elif (
            Cash.objects.filter(pk=id_cash)[0].income_item == "--КУ Бизнес--"
            or Cash.objects.filter(pk=id_cash)[0].income_item == "--КУ Мероприятия--"
        ):
            motivation_business = {
                "account": {"junior": 0.18, "middle": 0.21, "senior": 0.23},
                "marketer": {
                    "old": {"junior": 0.12, "middle": 0.328},
                    "new": {"junior": 0.12, "middle": 0.3},
                },
                "sales": {"new": 0.141},
                "rom": 0.075,
                "roa": 0.075,
            }
            if form_list_accounts.is_valid():
                employee_id_account = form_list_accounts.cleaned_data["account_manager"]
                if (
                    Employee.objects.filter(pk=int(employee_id_account))[0].post_name
                    == "Аккаунт-менеджер (junior)"
                ):
                    payment = (
                        Cash.objects.filter(pk=id_cash)[0].income
                        * motivation_business["account"]["junior"]
                    )
                    Payment.objects.create(
                        date_time=datetime.date.today(),
                        employee_id=Employee.objects.filter(pk=employee_id_account)[0],
                        payment=payment,
                        comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation_business['account']['junior']}",
                    )
                elif (
                    Employee.objects.filter(pk=int(employee_id_account))[0].post_name
                    == "Аккаунт-менеджер (middle)"
                ):
                    payment = (
                        Cash.objects.filter(pk=id_cash)[0].income
                        * motivation_business["account"]["middle"]
                    )
                    Payment.objects.create(
                        date_time=datetime.date.today(),
                        employee_id=Employee.objects.filter(pk=employee_id_account)[0],
                        payment=payment,
                        comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation_business['account']['middle']}",
                    )

                elif (
                    Employee.objects.filter(pk=int(employee_id_account))[0].post_name
                    == "Аккаунт-менеджер (senior)"
                ):
                    payment = (
                        Cash.objects.filter(pk=id_cash)[0].income
                        * motivation_business["account"]["senior"]
                    )
                    Payment.objects.create(
                        date_time=datetime.date.today(),
                        employee_id=Employee.objects.filter(pk=employee_id_account)[0],
                        payment=payment,
                        comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation_business['account']['senior']}",
                    )

            if form_list_marketers.is_valid():
                employee_id_marketer = form_list_marketers.cleaned_data[
                    "marketer_manager"
                ]
                if (
                    Employee.objects.filter(pk=int(employee_id_marketer))[0].post_name
                    == "Младший маркетолог"
                ):
                    if (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Старая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation_business["marketer"]["old"]["junior"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                        k = {motivation_business['marketer']['old']['junior']}",
                        )
                    elif (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Новая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation_business["marketer"]["new"]["junior"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                        k = {motivation_business['marketer']['new']['junior']}",
                        )

                elif (
                    Employee.objects.filter(pk=int(employee_id_marketer))[0].post_name
                    == "Интернет-маркетолог"
                ):
                    if (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Старая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation_business["marketer"]["old"]["middle"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                    k = {motivation_business['marketer']['old']['middle']}",
                        )
                    elif (
                        Employee.objects.filter(pk=int(employee_id_marketer))[
                            0
                        ].motivation_type
                        == "Новая"
                    ):
                        payment = (
                            Cash.objects.filter(pk=id_cash)[0].income
                            * motivation_business["marketer"]["new"]["middle"]
                        )
                        Payment.objects.create(
                            date_time=datetime.date.today(),
                            employee_id=Employee.objects.filter(
                                pk=int(employee_id_marketer)
                            )[0],
                            payment=payment,
                            comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                    k = {motivation_business['marketer']['new']['middle']}",
                        )
            if form_list_sales.is_valid():
                employee_id_sales = form_list_sales.cleaned_data["sales_manager"]
                payment = (
                    Cash.objects.filter(pk=id_cash)[0].income
                    * motivation_business["sales"]["new"]
                )
                Payment.objects.create(
                    date_time=datetime.date.today(),
                    employee_id=Employee.objects.filter(pk=int(employee_id_sales))[0],
                    payment=payment,
                    comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                                    k = {motivation_business['sales']['new']}",
                )
            # Платеж РОМу
            payment_rom = (
                Cash.objects.filter(pk=id_cash)[0].income * motivation_business["rom"]
            )
            Payment.objects.create(
                date_time=datetime.date.today(),
                employee_id=Employee.objects.filter(post_name="РОМ")[0],
                payment=payment_rom,
                comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation_business['rom']}",
            )
            # Платеж РОА
            payment_roa = (
                Cash.objects.filter(pk=id_cash)[0].income * motivation_business["roa"]
            )
            Payment.objects.create(
                date_time=datetime.date.today(),
                employee_id=Employee.objects.filter(post_name="РОА")[0],
                payment=payment_roa,
                comment=f"Выплата с поступления {Cash.objects.filter(pk=id_cash)[0].client_id.client_name}, \
                        k = {motivation_business['roa']}",
            )

            status = Cash.objects.get(pk=id_cash)
            status.status = "Оплачено сотрудникам"
            status.save()

        return render(request, "salary/success_message.html")


class AllEmployees(View):
    """Показывает страницу со всеми сотрудниками"""

    def get(self, request):
        form = AddEmployee()
        employees = Employee.objects.order_by('status', 'department_id_id', 'last_name')
        paginator = Paginator(employees, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"page_obj": page_obj, "form": form}
        return render(request, "salary/all_employees.html", context=context)

    def post(self, request):
        form = AddEmployee(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/employees")
        else:
            return render(request, "salary/error_message.html")


class AllCash(View):
    """Показывает страницу со всеми поступлениями"""

    def get(self, request):
        form = AddCash()
        filtered_qs = CashFilter(
            request.GET, queryset=Cash.objects.order_by("-date_time")
        ).qs
        paginator = Paginator(filtered_qs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        form_list_accounts = AccountsListForm()
        form_list_marketers = MarketersListForm()
        cash_filter = CashFilter(request.GET, queryset=filtered_qs)
        context = {
            "page_obj": page_obj,
            "form": form,
            "cash_filter": cash_filter,
            "form_list_accounts": form_list_accounts,
            "form_list_marketers": form_list_marketers,
        }
        return render(request, "salary/all_cash.html", context=context)

    def post(self, request):
        form = AddCash(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/cash")
        else:
            return render(request, "salary/error_message.html")


class AllPayments(View):
    """Показывает страницу со всеми расходами"""

    def get(self, request):
        form = AddPayment()
        filtered_qs = PaymentFilter(
            request.GET,
            queryset=Payment.objects.order_by("-date_time").filter(status="Оплачено"),
        ).qs
        paginator = Paginator(filtered_qs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        payment_filter = PaymentFilter(request.GET, queryset=filtered_qs)
        context = {
            "page_obj": page_obj,
            "form": form,
            "payment_filter": payment_filter,
        }
        return render(request, "salary/all_payments.html", context=context)

    def post(self, request):
        form = AddPayment(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/payments")
        else:
            return render(request, "salary/error_message.html")


class UpdateFormClient(UpdateView):
    """Редактирование формы клиента"""

    model = Client
    form_class = AddClient
    template_name = "salary/edit_client_form.html"
    success_url = "/clients"


class CreateFormClient(CreateView):
    """Создание формы клиента"""

    model = Client
    form_class = AddClient
    template_name = "salary/add_client_form.html"
    success_url = "/clients"


class UpdateFormEmployee(UpdateView):
    """Редактирование формы сотрудника"""

    model = Employee
    form_class = AddEmployee
    template_name = "salary/edit_employee_form.html"
    success_url = "/employees"


class CreateFormEmployee(CreateView):
    """Создание формы сотрудника"""

    model = Employee
    form_class = AddEmployee
    template_name = "salary/add_employee_form.html"
    success_url = "/employees"


class UpdateFormCash(UpdateView):
    """Редактирование формы поступления"""

    model = Cash
    form_class = AddCash
    template_name = "salary/edit_cash.html"
    success_url = "/cash"


class CreateFormCash(CreateView):
    """Создание формы поступления"""

    model = Cash
    form_class = AddCash
    template_name = "salary/add_cash.html"
    success_url = "/cash"


class UpdateFormPayEmployee(UpdateView):
    """Редактирование формы оплаты сотруднику"""

    model = Payment
    form_class = AddPayment
    template_name = "salary/edit_payment.html"
    success_url = "/employees"


class CreateFormPayEmployee(CreateView):
    """Создание формы оплаты сотруднику"""

    model = Payment
    form_class = AddPayment
    template_name = "salary/add_payment.html"
    success_url = "/employees"


class Calendar(View):
    """Платежный календарь"""
    def get(self, request):
        # Может работать неправильно.. Обнуляет платежный календарь, если поменялся месяц
        previous_month = Cash.objects.latest('id').date_time.month
        if datetime.date.today().month != previous_month:
            for elem in StaticCost.objects.all():
                elem.cost_sum = 0
                elem.save()
            for elem in StaticCash.objects.all():
                elem.cash_sum = 0
                elem.save()
            for elem in Tax.objects.all():
                elem.tax_sum = 0
                elem.save()

        static_cost = StaticCost.objects.all()
        static_cash = StaticCash.objects.all()
        taxes = Tax.objects.all()
        total_cost = 0
        total_cash = 0
        for elem in static_cost:
            total_cost += elem.cost_sum
        for elem in static_cash:
            total_cash += elem.cash_sum
        date = datetime.date.today()
        clients_previous_month = Cash.objects.filter(
            date_time__contains=f"{datetime.datetime.now().year}-{datetime.datetime.now().month-1}"
        )
        total_clients_previous_month = 0
        for elem in clients_previous_month:
            total_clients_previous_month += elem.income
        context = {
            "static_cost": static_cost,
            "static_cash": static_cash,
            "taxes": taxes,
            "date": date,
            "total_cost": total_cost,
            "total_cash": total_cash,
            "clients_previous_month": clients_previous_month,
            "total_clients_previous_month": total_clients_previous_month,
        }
        return render(request, "salary/calendar.html", context=context)


class RegisterUser(CreateView):
    """Регистрация нового пользователя"""

    model = User
    form_class = RegistrationUserForm
    template_name = "salary/registration.html"
    success_url = "/login"

    def form_valid(self, form):
        if form.is_valid():
            Employee.objects.create(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                post_name=form.cleaned_data["post_name"],
                department_id=Department.objects.get(
                    name_department=form.cleaned_data["department"]
                ),
                motivation_type="Новая",
                comment="",
                status="Работает",
                date_admission=datetime.datetime.today().date().strftime("%Y-%m-%d")
            )
            return super(RegisterUser, self).form_valid(form)

    def get_success_url(self):
        return reverse("all_employees")


class LoginUser(LoginView):
    """Вход на сайт под пользователем"""

    model = User
    form_class = AuthenticationForm
    template_name = "salary/login.html"

    def get_success_url(self):
        return reverse("all_employees")


def logout_user(request):
    """Выход с сайта"""
    logout(request)
    return HttpResponseRedirect("/login")


class AddStaticCash(View):
    """Добавляет сумму к постоянным доходам"""

    def get(self, request, pk):
        return render(
            request,
            "salary/add_sum_form.html",
        )

    def post(self, request, pk):
        cash_sum = request.POST.get("sum", False)
        static_cash_object = get_object_or_404(StaticCash, id=pk)
        static_cash_object.cash_sum += int(cash_sum)
        static_cash_object.save()
        return HttpResponseRedirect("/payment_calendar")


class AddStaticCost(View):
    """Добавляет сумму к постоянным расходам"""

    def get(self, request, pk):
        return render(
            request,
            "salary/add_sum_form.html",
        )

    def post(self, request, pk):
        cost_sum = request.POST.get("sum", False)
        static_cost_object = get_object_or_404(StaticCost, id=pk)
        static_cost_object.cost_sum += int(cost_sum)
        static_cost_object.save()
        return HttpResponseRedirect("/payment_calendar")


class AddTax(View):
    """Добавляет сумму к налогам"""

    def get(self, request, pk):
        return render(
            request,
            "salary/add_sum_form.html",
        )

    def post(self, request, pk):
        tax_sum = request.POST.get("sum", False)
        tax_object = get_object_or_404(Tax, id=pk)
        tax_object.tax_sum += int(tax_sum)
        tax_object.save()
        return HttpResponseRedirect("/payment_calendar")


def refresh_cash(request):
    """Кнопка обновления платежей"""
    headers = {
        "Authorization": "TOKEN",
        "Content-Type": "application/json",
    }
    from_date = Cash.objects.latest('id').date_time.strftime("%Y-%m-%d")
    till_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
    requests_cash = requests.get(
        f"https://business.tinkoff.ru/openapi/api/v1/bank-statement?accountNumber={account}&from={from_date}&till={till_date}",
        headers=headers,
        verify=False,
    )
    operations = requests_cash.json()["operation"]

    for i in range(len(operations)):
        if operations[i]["payerAccount"] != {account}:
            if operations[i]["operationId"] not in Cash.objects.all().values_list(
                "operation_id", flat=True
            ):
                if operations[i]["payerInn"] not in Client.objects.all().values_list(
                    "client_inn", flat=True
                ):
                    name = operations[i]["payerName"]
                    if '"' in name:
                        client_name = name[name.find('"') + 1 : -1]
                    elif "ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ" in name.upper():
                        name = name.upper()
                        client_name = name.removeprefix(
                            "ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ "
                        )
                    elif "ИП" in name.upper():
                        name = name.upper()
                        client_name = name.removeprefix("ИП ")
                    else:
                        client_name = name

                    Client.objects.create(
                        client_name=client_name,
                        official_name=operations[i]["payerName"],
                        is_still_client="Работаем",
                        client_inn=operations[i]["payerInn"],
                    )
                name_client = Client.objects.filter(
                    client_inn=operations[i]["payerInn"]
                )[0]

                Cash.objects.create(
                    date_time=operations[i]["date"],
                    income=operations[i]["amount"],
                    income_item=operations[i]["paymentPurpose"],
                    client_id=name_client,
                    operation_id=operations[i]["operationId"],
                )
    return HttpResponseRedirect("/cash")
