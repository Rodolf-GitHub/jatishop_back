# Generated by Django 5.1.4 on 2025-01-10 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_tiendatema'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategoria',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='subcategorias/'),
        ),
    ]
