# Generated by Django 4.1.3 on 2022-11-30 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0022_staticcash_staticcost_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticcash',
            name='date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='staticcost',
            name='date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]