# Generated by Django 4.1.3 on 2022-11-09 14:03

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0014_alter_product_productowner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='productowner',
            field=models.CharField(default='ihamegrbt@gmail.com', max_length=300, verbose_name=django.contrib.auth.models.AbstractUser.get_full_name),
        ),
    ]
