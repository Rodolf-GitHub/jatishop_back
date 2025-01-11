from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils.text import slugify
from colorfield.fields import ColorField
import re
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class InfoNegocio(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, editable=False)  # No editable, se genera automáticamente
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='negocios/logos/', blank=True, null=True)
    img_portada = models.ImageField(upload_to='negocios/img_portada/', blank=True, null=True)
    favicon = models.ImageField(upload_to='negocios/favicons/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Redes sociales
    whatsapp = models.URLField(blank=True, null=True)    
    # Horario
    horario = models.TextField(help_text="Horario de atención")
    
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Procesar latitud y longitud para aceptar punto o coma
        if self.latitud:
            self.latitud = str(self.latitud).replace('.', ',')
        if self.longitud:
            self.longitud = str(self.longitud).replace('.', ',')
        
        super().clean()

    def save(self, *args, **kwargs):
        # Convertir comas a puntos antes de guardar
        if self.latitud:
            self.latitud = str(self.latitud).replace(',', '.')
        if self.longitud:
            self.longitud = str(self.longitud).replace(',', '.')
            
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'

    def __str__(self):
        return self.nombre

class NegocioUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    negocio = models.ForeignKey(InfoNegocio, on_delete=models.CASCADE)

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

class Producto(models.Model):
    nombre = models.CharField(max_length=200,unique=True)
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
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
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

    def __str__(self):
        return self.nombre

    @property
    def precio_con_descuento(self):
        if self.descuento > 0:
            descuento = (self.precio * self.descuento) / 100
            return self.precio - descuento
        return self.precio

    def save(self, *args, **kwargs):
        # Redimensionar imagen si es necesario
        if self.imagen:
            img = Image.open(self.imagen)
            img_format = img.format
            
            # Redimensionar la imagen si es mayor a 5 KB
            while True:
                img_io = BytesIO()
                img.save(img_io, format=img_format, quality=85)  # Ajusta la calidad según sea necesario
                img_size = img_io.getbuffer().nbytes
                
                if img_size <= 5 * 1024:  # 5 KB
                    break
                img = img.resize((int(img.width * 0.9), int(img.height * 0.9)))  # Reducir tamaño

            self.imagen.save(self.imagen.name, ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)

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