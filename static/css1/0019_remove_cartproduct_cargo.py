# Generated by Django 4.1.3 on 2022-11-10 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0018_alter_cartproduct_cargo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartproduct',
            name='cargo',
        ),
    ]