# Generated by Django 4.1.3 on 2022-11-30 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0021_staticcost_alter_cash_income_item_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticCash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=None)),
                ('cash_name', models.CharField(default=None, max_length=200)),
                ('cash_sum', models.PositiveIntegerField()),
                ('comment', models.CharField(blank=True, default=None, max_length=200, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='staticcost',
            name='date',
            field=models.DateField(default=None),
        ),
    ]
