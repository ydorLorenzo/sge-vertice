# Generated by Django 2.0.2 on 2019-12-10 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ges_trab', '0002_auto_20190509_1122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trabajador',
            name='sancionado',
        ),
        migrations.RemoveField(
            model_name='trabajador',
            name='tec_tac',
        ),
        migrations.RemoveField(
            model_name='trabajador',
            name='tipo_tecnico',
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='escolaridad',
            field=models.CharField(choices=[('6to', '6to Grado'), ('9no ', '9no Grado'), ('12mo ', '12mo Grado'), ('TM', 'Técnico Medio'), ('OC', 'Obrero Calificado'), ('Univ', 'Universitario'), ('FOC', 'Facultad Obrero Campesino')], max_length=20, verbose_name='Escolaridad'),
        ),
    ]
