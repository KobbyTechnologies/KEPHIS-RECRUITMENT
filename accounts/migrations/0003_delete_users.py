# Generated by Django 3.2.9 on 2022-10-21 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_users_email'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Users',
        ),
    ]
