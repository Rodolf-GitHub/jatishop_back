from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone

class Billetera(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='billetera'
    )
    saldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    codigo_referido = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )
    referido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referidos'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Billetera'
        verbose_name_plural = 'Billeteras'

    def __str__(self):
        return f"Billetera de {self.usuario.email}"

    def agregar_saldo(self, cantidad):
        """Añade saldo a la billetera"""
        self.saldo += Decimal(str(cantidad))
        self.save()

class TransaccionBilletera(models.Model):
    billetera = models.ForeignKey(
        Billetera,
        on_delete=models.CASCADE,
        related_name='transacciones'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    saldo_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    saldo_posterior = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    referido_negocio = models.ForeignKey(
        'InfoNegocio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones_referido'
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Transacción de Billetera'
        verbose_name_plural = 'Transacciones de Billetera'

    def __str__(self):
        return f"Transacción de ${self.monto} - {self.fecha}"

    def save(self, *args, **kwargs):
        # Guardar saldo anterior
        if not self.pk:  # Si es una nueva transacción
            self.saldo_anterior = self.billetera.saldo
            self.billetera.saldo += self.monto
            self.saldo_posterior = self.billetera.saldo
            self.billetera.save()
            
        super().save(*args, **kwargs)
