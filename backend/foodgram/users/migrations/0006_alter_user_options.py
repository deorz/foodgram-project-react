# Generated by Django 4.1 on 2022-08-14 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_subscription_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('-date_joined',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]
