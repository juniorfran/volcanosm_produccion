# Generated by Django 4.2.9 on 2024-05-08 19:17

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accesos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=250)),
                ('cant_usuarios', models.IntegerField(null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, null=True)),
                ('fecha_expiracion', models.DateTimeField(null=True)),
                ('estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('direccion', models.TextField()),
                ('dui', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('telefono', models.CharField(max_length=20)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EnlacePagoAcceso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comercio_id', models.CharField(max_length=500)),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nombre_producto', models.CharField(max_length=500)),
                ('url_qr_code', models.URLField()),
                ('url_enlace', models.URLField()),
                ('esta_productivo', models.BooleanField()),
                ('descripcionProducto', ckeditor.fields.RichTextField()),
                ('cantidad', models.CharField(max_length=5)),
                ('imagenProducto', models.URLField(max_length=250, null=True)),
                ('idEnlace', models.CharField(max_length=150)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('acceso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enlace_pago_set', to='Internet.accesos')),
            ],
        ),
        migrations.CreateModel(
            name='Tipos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, null=True)),
                ('tiempo_conexion', models.CharField(max_length=50, null=True)),
                ('velocidad_mb', models.CharField(max_length=50, null=True)),
                ('descripcion', models.CharField(max_length=250, null=True)),
                ('precio', models.DecimalField(decimal_places=4, max_digits=5, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, null=True)),
                ('imagen_tipo', models.ImageField(null=True, upload_to='tipos_accesos')),
                ('url_azure', models.URLField(blank=True, max_length=400, null=True)),
                ('fecha_inicio', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('fecha_fin', models.DateTimeField(default=django.utils.timezone.now, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransaccionCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, null=True)),
                ('estado', models.BooleanField(default=True)),
                ('acceso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaccion_set', to='Internet.accesos')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaccion_set', to='Internet.clientes')),
                ('enlace_pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Internet.enlacepagoacceso')),
            ],
        ),
        migrations.AddField(
            model_name='accesos',
            name='acceso_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Internet.tipos'),
        ),
    ]