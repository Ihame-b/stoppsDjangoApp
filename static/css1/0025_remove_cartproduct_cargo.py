# Generated by Django 4.1.3 on 2022-11-10 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0024_alter_cartproduct_cargo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartproduct',
            name='cargo',
        ),
    ]