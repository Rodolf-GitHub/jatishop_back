# Generated by Django 5.1.4 on 2025-01-13 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_infonegocio_acepta_transferencia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='infonegocio',
            name='municipio',
            field=models.CharField(default='Jatibonico', max_length=50, verbose_name='Municipio'),
        ),
        migrations.AddField(
            model_name='infonegocio',
            name='provincia',
            field=models.CharField(choices=[('Pinar del Río', 'Pinar del Río'), ('Artemisa', 'Artemisa'), ('La Habana', 'La Habana'), ('Mayabeque', 'Mayabeque')], default='Sancti Spíritus', max_length=50, verbose_name='Provincia'),
        ),
    ]
