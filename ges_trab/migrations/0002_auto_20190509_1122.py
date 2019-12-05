# Generated by Django 2.0.2 on 2019-05-09 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ges_trab', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajador',
            name='motivo_alta',
            field=models.CharField(blank=True, default='Ocupar plaza vacante', max_length=60, null=True, verbose_name='Motivo Alta'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='orga_defensa',
            field=models.CharField(choices=[('MTT', 'MTT'), ('FEI', 'FEI'), ('BPD-LR ', 'BPD-LR'), ('BPD-PTG ', 'BPD-PTG'), ('U/R', 'U/R'), ('Imp', 'Imprescindible')], max_length=20, verbose_name='Organización defensa'),
        ),
    ]
