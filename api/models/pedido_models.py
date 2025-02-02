from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from .producto_models import Producto
from .negocio_models import InfoNegocio

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado')
    ]

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta')
    ]

    # Información del cliente
    nombre_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    direccion_entrega = models.TextField()
    
    # Información del pedido
    negocio = models.ForeignKey(
        InfoNegocio,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    productos = models.ManyToManyField(
        Producto,
        through='PedidoProducto',
        related_name='pedidos',
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='efectivo'
    )
    nota_comprador = models.TextField(blank=True)
    nota_vendedor = models.TextField(blank=True)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente}"

    def clean(self):
        """Validar que el pedido tenga al menos un producto"""
        super().clean()
        # Verificar si es un nuevo pedido (sin ID)
        if not self.pk:
            return
        
        # Verificar si tiene productos
        if not self.items.exists():
            raise ValidationError({
                'productos': 'El pedido debe tener al menos un producto.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def calcular_total(self):
        """Calcular el total del pedido"""
        if not self.items.exists():
            raise ValidationError('No se puede calcular el total sin productos')
            
        total = sum(
            item.cantidad * item.precio_unitario 
            for item in self.items.all()
        )
        self.total = total
        self.save()
        return total

class PedidoProducto(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='items_pedido'
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Pedido #{self.pedido.id}"

    def clean(self):
        """Validar cantidad y precio"""
        super().clean()
        if self.cantidad < 1:
            raise ValidationError({
                'cantidad': 'La cantidad debe ser mayor a 0.'
            })
        if self.precio_unitario <= 0:
            raise ValidationError({
                'precio_unitario': 'El precio debe ser mayor a 0.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        # Guardar el precio actual del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_con_descuento
        
        # Calcular subtotal
        self.subtotal = Decimal(str(self.cantidad)) * self.precio_unitario
        
        super().save(*args, **kwargs)
        
        # Recalcular total del pedido
        self.pedido.calcular_total()
