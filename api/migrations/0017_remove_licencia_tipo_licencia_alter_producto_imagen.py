# Generated by Django 4.2 on 2025-02-06 21:43

import api.models.producto_models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_licencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='licencia',
            name='tipo_licencia',
        ),
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, default='default/default_producto.jfif', max_length=500, null=True, upload_to=api.models.producto_models.Producto.producto_imagen_path),
        ),
    ]
