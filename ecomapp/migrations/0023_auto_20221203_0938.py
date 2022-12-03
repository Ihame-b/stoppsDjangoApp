# Generated by Django 3.2.5 on 2022-12-03 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0022_auto_20221203_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='CampanyName',
            field=models.CharField(choices=[('LINFOX', 'linfox'), ('KBS', 'kbs'), ('OTHERS', 'others')], default='LINFOX', max_length=20),
        ),
        migrations.AlterField(
            model_name='cargo',
            name='address',
            field=models.CharField(blank=True, default=' ', max_length=100, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='cargo',
            name='cargo_status',
            field=models.CharField(choices=[('Cargo Available', 'Cargo Available'), ('Cargo Not Available', 'Cargo Not Available')], default=' ', max_length=50),
        ),
    ]
