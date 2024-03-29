# Generated by Django 4.2.9 on 2024-02-01 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tours', '0015_alter_reserva_iva'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagentour',
            name='url_azure',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='imagentour',
            name='imagen',
            field=models.ImageField(upload_to='tours'),
        ),
        migrations.AlterField(
            model_name='imagentour',
            name='imagen1',
            field=models.ImageField(upload_to='tours'),
        ),
        migrations.AlterField(
            model_name='imagentour',
            name='imagen2',
            field=models.ImageField(upload_to='tours'),
        ),
        migrations.AlterField(
            model_name='imagentour',
            name='imagen3',
            field=models.ImageField(upload_to='tours'),
        ),
    ]
