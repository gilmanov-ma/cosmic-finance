from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Employee, Client, Cash, Payment, Department
from django import forms


class DateInput(forms.DateInput):
    input_type = "date"


class AddClient(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"


class EditStatusClient(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["is_still_client"]


class EditStatusPayment(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["status"]


class AddEmployee(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"


class AddCash(forms.ModelForm):
    class Meta:
        widgets = {"date_time": DateInput()}
        model = Cash
        fields = "__all__"


class AddPayment(forms.ModelForm):
    class Meta:
        widgets = {"date_time": DateInput()}
        model = Payment
        fields = "__all__"


# creating a form
class AccountsListForm(forms.Form):
    ACCOUNT_CHOICES = Employee.objects.filter(
        department_id=Department.objects.get(name_department="Отдел сопровождения клиентов (аккаунт)")
    )
    account_list = (
        (elem.pk, f"{elem.first_name} {elem.last_name}") for elem in ACCOUNT_CHOICES
    )
    account_manager = forms.ChoiceField(choices=account_list)


class MarketersListForm(forms.Form):
    MARKETER_CHOICES = Employee.objects.filter(
        department_id=Department.objects.get(name_department="Отдел маркетинга")
    )
    marketer_list = (
        (elem.pk, f"{elem.first_name} {elem.last_name}") for elem in MARKETER_CHOICES
    )
    marketer_manager = forms.ChoiceField(choices=marketer_list)


class SalesListForm(forms.Form):
    SALES_CHOICES = Employee.objects.filter(
        department_id=Department.objects.get(name_department="Отдел продаж")
    )
    sales_list = (
        (elem.pk, f"{elem.first_name} {elem.last_name}") for elem in SALES_CHOICES
    )
    sales_manager = forms.ChoiceField(choices=sales_list)


class RegistrationUserForm(UserCreationForm):
    POST_CHOICES = [
        ("Менеджер по продажам", "Менеджер по продажам"),
        ("Аккаунт-менеджер (junior)", "Аккаунт-менеджер (junior)"),
        ("Аккаунт-менеджер (middle)", "Аккаунт-менеджер (middle)"),
        ("Аккаунт-менеджер (senior)", "Аккаунт-менеджер (senior)"),
        ("Младший маркетолог", "Младший маркетолог"),
        ("Интернет-маркетолог", "Интернет-маркетолог"),
        ("Call-оператор", "Call-оператор"),
        ("Верстальщик", "Верстальщик"),
        ("Дизайнер", "Дизайнер"),
        ("Специалист по PR", "Специалист по PR"),
        ("Рекрутер", "Рекрутер"),
        ("CRM-менеджер", "CRM-менеджер"),
        ("РОА", "РОА"),
        ("РОМ", "РОМ"),
        ("Ассистент директора, бухгалтер", "Ассистент директора, бухгалтер"),
    ]

    DEPARTMENT_CHOICES = [
        ('Менеджмент', "Менеджмент"),
        ("Отдел продаж", "Отдел продаж"),
        ("Отдел маркетинга", "Отдел маркетинга"),
        ("Отдел по сопровождению клиентов (аккаунт)", "Отдел по сопровождению клиентов (аккаунт)"),
        ("IT отдел", "IT отдел"),
    ]

    username = forms.CharField(
        label="Логин", widget=forms.TextInput(attrs={"class": "form-input"})
    )
    first_name = forms.CharField(
        label="Имя (вводите правильно)",
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    last_name = forms.CharField(
        label="Фамилия (вводите правильно)",
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    post_name = forms.ChoiceField(
        label = "Ваша должность",
        choices=POST_CHOICES,
    )
    department = forms.ChoiceField(
        label = "Ваша отдел",
        choices=DEPARTMENT_CHOICES
    )
    class Meta:
        model = User
        fields = ("username", "password1", "password2", "first_name", "last_name", "post_name", "department")

