from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from colorfield.fields import ColorField
import os
from ..ubicaciones_cuba import PROVINCIAS, get_municipios
from django.core.exceptions import ValidationError

class InfoNegocio(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    descripcion = models.TextField(blank=True, null=True, default="Este negocio aún no tiene descripción")
    direccion = models.CharField(max_length=255, blank=True, null=True, default="Este negocio aún no ha configurado su dirección")
    telefono = models.CharField(max_length=20, blank=True, null=True, default="Sin teléfono")
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='negocios/logos/', blank=True, null=True, default='default/default_logo.jpg')
    img_portada = models.ImageField(upload_to='negocios/img_portada/', blank=True, null=True, default='default/default_portada.jpg')
    activo = models.BooleanField(default=True)
    hace_domicilio = models.BooleanField(default=False)
    acepta_transferencia = models.BooleanField(default=False)
    MONEDA_PRINCIPAL_CHOICES = (
        ('CUP', 'CUP'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('ZELLE', 'ZELLE'),
        ('MLC', 'MLC'),
    )
    moneda_principal = models.CharField(
        max_length=5,
        choices=MONEDA_PRINCIPAL_CHOICES,
        default='CUP',
        blank=True,
        null=True
    )
    
    whatsapp = models.URLField(blank=True, null=True)    
    horario = models.TextField(blank=True, null=True, default="Este negocio aún no ha configurado su horario", help_text="Horario de atención")
    
    latitud = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        help_text="Ejemplo: 21.123456 o 21,123456"
    )
    longitud = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        help_text="Ejemplo: -82.123456 o -82,123456"
    )
    
    provincia = models.CharField(
        max_length=50,
        choices=[(p, p) for p in PROVINCIAS],
        verbose_name='Provincia',
        default='Sancti Spíritus',
        blank=True,
        null=True
    )
    
    municipio = models.CharField(
        max_length=50,
        verbose_name='Municipio',
        default='Jatibonico',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.latitud:
            self.latitud = str(self.latitud).replace('.', ',')
        if self.longitud:
            self.longitud = str(self.longitud).replace('.', ',')
        
        super().clean()
        if self.provincia and self.municipio:
            municipios_validos = get_municipios(self.provincia)
            if self.municipio not in municipios_validos:
                raise ValidationError({
                    'municipio': f'El municipio {self.municipio} no pertenece a la provincia {self.provincia}'
                })

    def save(self, *args, **kwargs):
        try:
            old_instance = InfoNegocio.objects.get(pk=self.pk)
            if old_instance.logo and self.logo != old_instance.logo:
                if os.path.isfile(old_instance.logo.path):
                    os.remove(old_instance.logo.path)
            if old_instance.img_portada and self.img_portada != old_instance.img_portada:
                if os.path.isfile(old_instance.img_portada.path):
                    os.remove(old_instance.img_portada.path)
        except InfoNegocio.DoesNotExist:
            pass

        if self.latitud:
            self.latitud = str(self.latitud).replace(',', '.')
        if self.longitud:
            self.longitud = str(self.longitud).replace(',', '.')
            
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.logo and os.path.isfile(self.logo.path):
            os.remove(self.logo.path)
        if self.img_portada and os.path.isfile(self.img_portada.path):
            os.remove(self.img_portada.path)
        super().delete(*args, **kwargs)

class NegocioUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='negocios_users')
    negocio = models.ForeignKey(InfoNegocio, on_delete=models.CASCADE, related_name='usuarios')

    class Meta:
        unique_together = ['user', 'negocio']

    def __str__(self):
        return f"{self.user.username} - {self.negocio.nombre}"

class TiendaTema(models.Model):
    negocio = models.OneToOneField(InfoNegocio, on_delete=models.CASCADE, related_name='tema')
    color_primario = ColorField(
        default='#8E44AD',
        verbose_name='Color Primario',
        help_text='Color principal de la tienda'
    )
    color_secundario = ColorField(
        default='#E67E22',
        verbose_name='Color Secundario',
        help_text='Color secundario de la tienda'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tema de Tienda'
        verbose_name_plural = 'Temas de Tiendas'

    def __str__(self):
        return f"Tema de {self.negocio.nombre}" 