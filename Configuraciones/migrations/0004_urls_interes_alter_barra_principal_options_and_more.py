# Generated by Django 4.2.9 on 2024-01-12 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Configuraciones', '0003_barra_principal_fecha_creacion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Urls_interes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('url', models.URLField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='barra_principal',
            options={'get_latest_by': 'fecha_creacion'},
        ),
        migrations.AlterModelOptions(
            name='contacts',
            options={'get_latest_by': 'fecha_creacion'},
        ),
        migrations.AlterField(
            model_name='urls_info',
            name='url',
            field=models.CharField(max_length=200),
        ),
    ]
