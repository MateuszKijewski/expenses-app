# Generated by Django 2.2.6 on 2019-11-01 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20191101_0004'),
    ]

    operations = [
        migrations.AddField(
            model_name='reccuringpayment',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]