# Generated by Django 2.0.2 on 2019-04-03 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_act', models.PositiveIntegerField()),
                ('descripcion_act', models.CharField(blank=True, max_length=100)),
                ('valor_prod_act', models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=9)),
                ('activa', models.BooleanField(default=True, editable=False)),
                ('numero', models.PositiveIntegerField(default=1, verbose_name='N&uacute;mero')),
                ('valor_act', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('prod_tecleada', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('venta', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.PositiveIntegerField()),
                ('nombre', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Inversionista',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_inv', models.CharField(max_length=12, unique=True)),
                ('nombre_inv', models.CharField(max_length=60)),
                ('direccion_inv', models.CharField(max_length=160)),
                ('municipio_sucursal_inv', models.CharField(max_length=20)),
                ('sucursal_mn_inv', models.CharField(max_length=60)),
                ('cuenta_mn_inv', models.CharField(max_length=16, unique=True)),
                ('sucursal_usd_inv', models.CharField(max_length=16)),
                ('cuenta_usd_inv', models.CharField(max_length=16, unique=True)),
                ('nit', models.CharField(max_length=11, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_ot', models.CharField(max_length=10, unique=True)),
                ('descripcion_ot', models.CharField(max_length=100)),
                ('no_contrato', models.CharField(max_length=5, unique=True)),
                ('valor_contrato', models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=9)),
                ('unidad', models.CharField(choices=[('03', 'USTI'), ('07', 'UGDD')], default='', max_length=4)),
                ('area', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='entrada_datos.Area')),
                ('inversionista', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='entrada_datos.Inversionista')),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=2, unique=True)),
                ('nombre', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Suplemento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=7)),
                ('fecha', models.DateField()),
                ('usuario', models.CharField(max_length=100)),
                ('solicitud', models.CharField(max_length=60)),
                ('orden_trab', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='entrada_datos.OT')),
            ],
        ),
        migrations.CreateModel(
            name='TipoActividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_tipo_act', models.CharField(max_length=60, unique=True)),
                ('valor', models.PositiveIntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnidadFacturacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_uf', models.CharField(max_length=12)),
                ('nombre_uf', models.CharField(max_length=60)),
                ('direccion_uf', models.CharField(max_length=160)),
                ('municipio_sucursal', models.CharField(max_length=10)),
                ('sucursal_mn', models.CharField(max_length=60)),
                ('cuenta_mn', models.CharField(max_length=16)),
                ('sucursal_usd', models.CharField(max_length=16)),
                ('cuenta_usd', models.CharField(max_length=16)),
                ('nit', models.CharField(max_length=11)),
            ],
        ),
        migrations.AddField(
            model_name='ot',
            name='tipo_servicio',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='entrada_datos.Servicio'),
        ),
        migrations.AddField(
            model_name='actividad',
            name='orden_trab',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='entrada_datos.OT'),
        ),
        migrations.AddField(
            model_name='actividad',
            name='tipo_act',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='entrada_datos.TipoActividad'),
        ),
    ]
