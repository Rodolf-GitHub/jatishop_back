from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from .categoria import Subcategoria

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(default=0)
    descuento = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(99)
        ]
    )
    
    def producto_imagen_path(instance, filename):
        return f'productos/{instance.subcategoria.categoria.negocio.slug}/{filename}'
    
    imagen = models.ImageField(
        upload_to=producto_imagen_path,
        blank=True, 
        null=True, 
        default='default/default_producto.jfif'
    )
    subcategoria = models.ForeignKey(
        Subcategoria,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.nombre and self.subcategoria_id:
            negocio = self.subcategoria.categoria.negocio
            productos_existentes = Producto.objects.filter(
                nombre__iexact=self.nombre,
                subcategoria__categoria__negocio=negocio
            )
            if self.pk:
                productos_existentes = productos_existentes.exclude(pk=self.pk)
            
            if productos_existentes.exists():
                raise ValidationError({
                    'nombre': 'Ya existe un producto con este nombre en este negocio'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        
        try:
            old_instance = Producto.objects.get(pk=self.pk)
            if old_instance.imagen and self.imagen != old_instance.imagen:
                if os.path.isfile(old_instance.imagen.path):
                    os.remove(old_instance.imagen.path)
        except Producto.DoesNotExist:
            pass

        if self.imagen:
            img = Image.open(self.imagen)
            img_format = img.format
            
            while True:
                img_io = BytesIO()
                img.save(img_io, format=img_format, quality=85)
                img_size = img_io.getbuffer().nbytes
                
                if img_size <= 20 * 1024:  # 20 KB
                    break
                img = img.resize((int(img.width * 0.9), int(img.height * 0.9)))

            self.imagen.save(self.imagen.name, ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    @property
    def precio_con_descuento(self):
        if self.descuento > 0:
            descuento = (self.precio * self.descuento) / 100
            return self.precio - descuento
        return self.precio

    def delete(self, *args, **kwargs):
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs) 