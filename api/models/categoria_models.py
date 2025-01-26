from django.db import models
import os
from .negocio_models import InfoNegocio

class Categoria(models.Model):
    negocio = models.ForeignKey(InfoNegocio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
        unique_together = ['negocio', 'nombre']

    def __str__(self):
        return f"{self.negocio.nombre} - {self.nombre}"

    def save(self, *args, **kwargs):
        try:
            old_instance = Categoria.objects.get(pk=self.pk)
            if old_instance.imagen and self.imagen != old_instance.imagen:
                if os.path.isfile(old_instance.imagen.path):
                    os.remove(old_instance.imagen.path)
        except Categoria.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

class Subcategoria(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE,
        related_name='subcategorias'
    )
    imagen = models.ImageField(upload_to='subcategorias/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        ordering = ['nombre']
        unique_together = ['nombre', 'categoria']

    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"

    def save(self, *args, **kwargs):
        try:
            old_instance = Subcategoria.objects.get(pk=self.pk)
            if old_instance.imagen and self.imagen != old_instance.imagen:
                if os.path.isfile(old_instance.imagen.path):
                    os.remove(old_instance.imagen.path)
        except Subcategoria.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs) 