# Generated by Django 4.1 on 2022-08-13 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_follow_subscription'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='subscription',
            table='Subscriptions',
        ),
    ]
