# Generated by Django 2.0.2 on 2019-08-26 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prenomina15', '0004_auto_20190823_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='obra',
            name='owner',
            field=models.CharField(default='admin', editable=False, max_length=20),
        ),
        migrations.AlterField(
            model_name='salariomax',
            name='grupo_esc',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='adm.EscalaSalarial'),
        ),
    ]
