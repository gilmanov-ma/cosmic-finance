# Generated by Django 4.1.3 on 2022-11-30 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0023_alter_staticcash_date_alter_staticcost_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticcost',
            name='date',
            field=models.DateField(blank=True, default='2022-05-01', null=True),
        ),
    ]