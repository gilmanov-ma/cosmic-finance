# Generated by Django 4.1.3 on 2022-11-30 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0020_cash_status_alter_cash_income_item_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_name', models.CharField(default=None, max_length=200)),
                ('cost_sum', models.PositiveIntegerField()),
                ('comment', models.CharField(blank=True, default=None, max_length=200, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='cash',
            name='income_item',
            field=models.CharField(choices=[('--КУ Стартап--', 'КУ Стартап'), ('--КУ Бизнес--', 'КУ Бизнес'), ('--КУ Мероприятия--', 'КУ Мероприятия'), ('Покупка лидов', 'Покупка лидов'), ('Лендинг (шаблон)', 'Лендинг (шаблон)'), ('Лендинг (уникальный)', 'Лендинг (уникальный)'), ('Разработка сайта', 'Разработка сайта'), ('Ведение соцсетей', 'Ведение соцсетей'), ('Управление репутацией', 'Управление репутацией'), ('Roistat', 'Roistat'), ('AmoCRM', 'AmoCRM'), ('Wazzup ', 'Wazzup '), ('Chat2Desk ', 'Chat2Desk '), ('Найм', 'Найм'), ('Roistat', 'Roistat'), ('Callback Hunter', 'Callback Hunter'), ('Прозвон лидов', 'Прозвон лидов'), ('Проверка CRM', 'Проверка CRM'), ('Тех. поддержка ', 'Тех. поддержка '), ('Roistat', 'Roistat'), ('Разработка презентации', 'Разработка презентации'), ('Разработка планировки', 'Разработка планировки'), ('Другое', 'Другое')], max_length=40),
        ),
        migrations.AlterField(
            model_name='employee',
            name='post_name',
            field=models.CharField(choices=[('Менеджер по продажам', 'Менеджер по продажам'), ('Аккаунт-менеджер (junior)', 'Аккаунт-менеджер (junior)'), ('Аккаунт-менеджер (middle)', 'Аккаунт-менеджер (middle)'), ('Аккаунт-менеджер (senior)', 'Аккаунт-менеджер (senior)'), ('Младший маркетолог', 'Младший маркетолог'), ('Интернет-маркетолог', 'Интернет-маркетолог'), ('Call-оператор', 'Call-оператор'), ('Верстальщик', 'Верстальщик'), ('Дизайнер', 'Дизайнер'), ('Специалист по PR', 'Специалист по PR'), ('Рекрутер', 'Рекрутер'), ('CRM-менеджер', 'CRM-менеджер'), ('РОА', 'РОА'), ('РОМ', 'РОМ'), ('Ассистент директора, бухгалтер', 'Ассистент директора, бухгалтер')], max_length=40),
        ),
    ]