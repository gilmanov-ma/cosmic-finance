from django.db import models
from django.urls import reverse
import datetime

# Create your models here.
class Department(models.Model):
    DEPARTMENT_CHOICES = [
        ('Менеджмент', "Менеджмент"),
        ("Отдел продаж", "Отдел продаж"),
        ("Отдел маркетинга", "Отдел маркетинга"),
        ("Отдел сопровождения клиентов (аккаунт)", "Отдел по сопровождения клиентов (аккаунт)"),
        ("IT отдел", "IT отдел"),
    ]
    name_department = models.CharField(max_length=40, choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return f"{self.name_department}"


class Employee(models.Model):
    TYPE_CHOICES = [
        ("Старая", "Старая"),
        ("Новая", "Новая"),
    ]
    EMPLOYEE_STATUS_CHOICES = [
        ("Работает", "Работает"),
        ("Уволен", "Уволен"),
    ]
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

    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    post_name = models.CharField(max_length=40, choices=POST_CHOICES)
    department_id = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
    comment = models.CharField(max_length=200, default=None, blank=True)
    motivation_type = models.CharField(
        max_length=40,
        default=TYPE_CHOICES[1][1],
        null=True,
        blank=True,
        choices=TYPE_CHOICES,
    )
    status = models.CharField(max_length=40, choices=EMPLOYEE_STATUS_CHOICES, default=EMPLOYEE_STATUS_CHOICES[0][1],
                              blank=True, null=True)
    date_admission = models.DateField(blank=False, default=datetime.datetime.today().date().strftime("%Y-%m-%d"))

    def get_url_employees(self):
        return reverse("employee_detail", args=[self.pk])

    def get_id_to_update(self):
        return reverse("update_employee", args=[self.pk])

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.post_name}"


class Client(models.Model):
    STATUS_CHOICES = [
        ("Работаем", "Работаем"),
        ("Не работаем", "Не работаем"),
        ("Непонятно", "Непонятно"),
    ]
    client_name = models.CharField(max_length=40, null=True, default=None)
    official_name = models.CharField(max_length=40, null=True, default=None)
    city = models.CharField(max_length=40, null=True, default=None)
    is_still_client = models.CharField(max_length=40, choices=STATUS_CHOICES)
    client_inn = models.CharField(max_length=12, null=True, default=None)

    def get_url_clients(self):
        return reverse("client_detail", args=[self.pk])

    def get_id_to_update(self):
        return reverse("update_client", args=[self.pk])

    def __str__(self):
        return f"{self.client_name}"


class Cash(models.Model):
    SERVICES = [
        ("--КУ Стартап--", "КУ Стартап"),
        ("--КУ Бизнес--", "КУ Бизнес"),
        ("--КУ Мероприятия--", "КУ Мероприятия"),
        ("Покупка лидов", "Покупка лидов"),
        ("Лендинг (шаблон)", "Лендинг (шаблон)"),
        ("Лендинг (уникальный)", "Лендинг (уникальный)"),
        ("Разработка сайта", "Разработка сайта"),
        ("Ведение соцсетей", "Ведение соцсетей"),
        ("Управление репутацией", "Управление репутацией"),
        ("Roistat", "Roistat"),
        ("AmoCRM", "AmoCRM"),
        ("Wazzup ", "Wazzup "),
        ("Chat2Desk ", "Chat2Desk "),
        ("Найм", "Найм"),
        ("Roistat", "Roistat"),
        ("Callback Hunter", "Callback Hunter"),
        ("Прозвон лидов", "Прозвон лидов"),
        ("Проверка CRM", "Проверка CRM"),
        ("Тех. поддержка ", "Тех. поддержка "),
        ("Roistat", "Roistat"),
        ("Разработка презентации", "Разработка презентации"),
        ("Разработка планировки", "Разработка планировки"),
        ("Другое", "Другое"),
    ]

    CASH_STATUS = [
        ("Распределить", "Распределить"),
        ("Оплачено сотрудникам", "Оплачено сотрудникам"),
    ]

    date_time = models.DateField(blank=False)
    income = models.PositiveIntegerField(blank=False)
    client_id = models.ForeignKey(
        Client, on_delete=models.PROTECT, default=None, blank=False
    )
    income_item = models.CharField(max_length=40, blank=False, choices=SERVICES)
    status = models.CharField(
        max_length=40, blank=False, default=CASH_STATUS[0][1], choices=CASH_STATUS
    )
    operation_id = models.CharField(max_length=40, blank=True, null=True, default='')

    def get_id_to_update(self):
        return reverse("update_cash", args=[self.pk])

    def get_url_cash(self):
        return reverse("cash_detail", args=[self.pk])

    def __str__(self):
        return f"{self.date_time} - {self.income} {self.income_item} {self.client_id}"


class Payment(models.Model):
    STATUS = [("Оплачено", "Оплачено"), ("На проверке", "На проверке")]
    date_time = models.DateField(blank=False)
    payment = models.PositiveIntegerField(blank=False)
    employee_id = models.ForeignKey(
        Employee, on_delete=models.PROTECT, default=None, blank=False
    )
    comment = models.CharField(max_length=200, null=True, default=None, blank=True)
    link = models.CharField(max_length=200, default=None, null=True, blank=True)
    status = models.CharField(
        max_length=40, blank=False, default=STATUS[1][1], choices=STATUS
    )

    def get_id_to_update(self):
        return reverse("update_payment", args=[self.pk])

    def get_id_to_change_status(self):
        return reverse("change_status", args=[self.pk])

    def __str__(self):
        return f"{self.date_time} - {self.payment} {self.employee_id}"


class StaticCost(models.Model):
    cost_name = models.CharField(max_length=200, null=False, default=None, blank=False)
    cost_sum = models.PositiveIntegerField(blank=False)
    comment = models.CharField(max_length=200, null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.cost_name} - {self.cost_sum}"

    def get_id_to_update(self):
        return reverse("add_static_cost", args=[self.pk])


class StaticCash(models.Model):
    cash_name = models.CharField(max_length=200, null=False, default=None, blank=False)
    cash_sum = models.PositiveIntegerField(blank=False)
    comment = models.CharField(max_length=200, null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.cash_name} - {self.cash_sum}"

    def get_id_to_update(self):
        return reverse("add_static_cash", args=[self.pk])


class Tax(models.Model):
    tax_name = models.CharField(max_length=200, null=False, default=None, blank=False)
    tax_sum = models.PositiveIntegerField(blank=False)
    comment = models.CharField(max_length=200, null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.tax_name} - {self.tax_sum}"

    def get_id_to_update(self):
        return reverse("add_tax", args=[self.pk])