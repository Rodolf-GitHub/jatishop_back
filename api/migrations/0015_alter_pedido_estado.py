# Generated by Django 4.2 on 2025-02-03 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_pedido_pedidoproducto_pedido_productos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmado', 'Confirmado'), ('en_proceso', 'En Proceso'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20),
        ),
    ]
