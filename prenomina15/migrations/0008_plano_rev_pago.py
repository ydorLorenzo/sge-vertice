# Generated by Django 2.0.2 on 2019-10-21 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prenomina15', '0007_auto_20190917_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='plano',
            name='rev_pago',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
    ]
