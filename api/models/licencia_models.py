from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

class Licencia(models.Model):
    negocio = models.OneToOneField(
        'InfoNegocio',
        on_delete=models.CASCADE,
        related_name='licencia'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    esta_activa = models.BooleanField(default=True)
    primera_licencia_pagada = models.BooleanField(
        default=False,
        help_text="Indica si el usuario ya pagó su primera licencia"
    )

    class Meta:
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'

    def __str__(self):
        return f"Licencia de {self.negocio.nombre}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)

        # Si es la primera vez que se paga la licencia
        if not self.primera_licencia_pagada and self.esta_activa:
            usuario = self.negocio.usuario
            if hasattr(usuario, 'billetera') and usuario.billetera.referido_por:
                try:
                    # Importar aquí para evitar importación circular
                    from ..models import TransaccionBilletera
                    
                    # Añadir $2 a la billetera del referidor
                    referidor_billetera = usuario.billetera.referido_por.billetera
                    TransaccionBilletera.objects.create(
                        billetera=referidor_billetera,
                        monto=Decimal('2.00'),
                        descripcion=f'Comisión por primera licencia de {self.negocio.nombre}',
                        referido_negocio=self.negocio
                    )
                    
                    # Marcar como pagada para que no se vuelva a pagar
                    self.primera_licencia_pagada = True
                    self.save()
                except Exception as e:
                    print(f"Error al procesar comisión de referido: {str(e)}")

    @property
    def dias_restantes(self):
        """Calcula los días restantes de la licencia"""
        if not self.esta_activa:
            return 0
        
        ahora = timezone.now()
        if ahora > self.fecha_vencimiento:
            return 0
            
        diferencia = self.fecha_vencimiento - ahora
        return diferencia.days

    def clean(self):
        """Validaciones adicionales"""
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now():
            raise ValidationError({
                'fecha_vencimiento': 'La fecha de vencimiento no puede ser en el pasado'
            })

    def activar(self):
        """Activa la licencia"""
        self.esta_activa = True
        self.save()

    def desactivar(self):
        """Desactiva la licencia"""
        self.esta_activa = False
        self.save()
