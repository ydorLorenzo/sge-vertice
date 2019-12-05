# Generated by Django 2.0.2 on 2019-04-03 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plantilla',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cant_plazas', models.PositiveIntegerField()),
                ('disponibles', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('cargo', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='adm.Cargo')),
                ('departamento', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='adm.Departamento')),
                ('unidad', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='adm.UnidadOrg')),
            ],
        ),
    ]
