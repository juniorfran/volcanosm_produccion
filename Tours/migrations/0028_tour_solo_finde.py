# Generated by Django 4.2.9 on 2024-11-15 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tours', '0027_enlacepagotour'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='solo_finde',
            field=models.BooleanField(default=False),
        ),
    ]