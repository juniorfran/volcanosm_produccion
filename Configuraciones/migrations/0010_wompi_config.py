# Generated by Django 4.2.9 on 2024-11-15 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Configuraciones', '0009_direccionamiento'),
    ]

    operations = [
        migrations.CreateModel(
            name='wompi_config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cuenta', models.CharField(blank=True, max_length=100, null=True)),
                ('client_id', models.CharField(blank=True, max_length=100, null=True)),
                ('client_secret', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
