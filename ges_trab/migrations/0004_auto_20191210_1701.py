# Generated by Django 2.0.2 on 2019-12-10 22:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ges_trab', '0003_auto_20191210_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajador',
            name='sal_plus',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Salario plus'),
        ),
    ]
