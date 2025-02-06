from django.db import models
from .negocio_models import InfoNegocio
from django.utils import timezone

class Licencia(models.Model):
    negocio = models.OneToOneField(InfoNegocio, on_delete=models.CASCADE, related_name='licencia')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    esta_activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Licencia de {self.negocio.nombre}"
    
    def dias_restantes(self):
        """
        Retorna días restantes si está activa,
        o días desde el vencimiento si está vencida
        """
        diferencia = self.fecha_vencimiento - timezone.now()
        if self.esta_activa:
            return max(0, diferencia.days)
        else:
            return abs(diferencia.days)
    
    def verificar_estado(self):
        if timezone.now() > self.fecha_vencimiento:
            self.esta_activa = False
            self.negocio.activo = False
            self.negocio.save()
            self.save()
        return self.esta_activa

    class Meta:
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'
