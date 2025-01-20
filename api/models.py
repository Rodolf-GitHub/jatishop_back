from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils.text import slugify
from colorfield.fields import ColorField
import re
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from .ubicaciones_cuba import PROVINCIAS, get_municipios
from django.core.exceptions import ValidationError

class InfoNegocio(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, editable=False)  # No editable, se genera automáticamente
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
    
    # Redes sociales
    whatsapp = models.URLField(blank=True, null=True)    
    # Horario
    horario = models.TextField(blank=True, null=True, default="Este negocio aún no ha configurado su horario", help_text="Horario de atención")
    
    # Ubicación
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

    def clean(self):
        # Procesar latitud y longitud para aceptar punto o coma
        if self.latitud:
            self.latitud = str(self.latitud).replace('.', ',')
        if self.longitud:
            self.longitud = str(self.longitud).replace('.', ',')
        
        super().clean()
        # Validar que el municipio pertenezca a la provincia
        if self.provincia and self.municipio:
            municipios_validos = get_municipios(self.provincia)
            if self.municipio not in municipios_validos:
                raise ValidationError({
                    'municipio': f'El municipio {self.municipio} no pertenece a la provincia {self.provincia}'
                })

    def save(self, *args, **kwargs):
        # Guardar las imágenes antiguas antes de actualizar
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

        # Convertir comas a puntos antes de guardar
        if self.latitud:
            self.latitud = str(self.latitud).replace(',', '.')
        if self.longitud:
            self.longitud = str(self.longitud).replace(',', '.')
            
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Eliminar archivos de imagen al eliminar el objeto
        if self.logo:
            if os.path.isfile(self.logo.path):
                os.remove(self.logo.path)
        if self.img_portada:
            if os.path.isfile(self.img_portada.path):
                os.remove(self.img_portada.path)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'

    def __str__(self):
        return self.nombre

class NegocioUser(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='negocios_users'
    )
    negocio = models.ForeignKey(
        InfoNegocio, 
        on_delete=models.CASCADE,
        related_name='usuarios'
    )

    class Meta:
        unique_together = ['user', 'negocio']  # Evita duplicados de usuario-negocio

    def __str__(self):
        return f"{self.user.username} - {self.negocio.nombre}"

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
        unique_together = ['negocio', 'nombre']  # Nombre único por negocio

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
        unique_together = ['nombre', 'categoria']  # Evita duplicados en la misma categoría

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
        # Construye la ruta: productos/nombre_negocio/filename
        return f'productos/{instance.subcategoria.categoria.negocio.slug}/{filename}'
    
    imagen = models.ImageField(
        upload_to=producto_imagen_path,  # Usa la función personalizada
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
        # Validar nombre único por negocio
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
                    'nombre': {
                        'code': 'producto_duplicado',
                        'message': f'Ya existe un producto llamado "{self.nombre}" en este negocio'
                    }
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Esto ejecutará el método clean()
        
        # Manejo de la imagen anterior
        try:
            old_instance = Producto.objects.get(pk=self.pk)
            if old_instance.imagen and self.imagen != old_instance.imagen:
                if os.path.isfile(old_instance.imagen.path):
                    os.remove(old_instance.imagen.path)
        except Producto.DoesNotExist:
            pass

        # Redimensionar imagen si es necesario
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

class TiendaTema(models.Model):
    negocio = models.OneToOneField(
        InfoNegocio, 
        on_delete=models.CASCADE, 
        related_name='tema'
    )
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