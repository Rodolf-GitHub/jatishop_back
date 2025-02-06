from rest_framework import serializers
from ...models import Pedido, PedidoProducto, Producto
from decimal import Decimal
from django.db import transaction

class PedidoProductoAdminSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = PedidoProducto
        fields = [
            'id', 'producto', 'producto_nombre', 
            'cantidad', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['subtotal']

class PedidoAdminSerializer(serializers.ModelSerializer):
    items = PedidoProductoAdminSerializer(many=True, read_only=True)
    productos = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'nombre_cliente', 'email_cliente',
            'direccion_entrega', 'nota_comprador', 'total', 'estado',
            'fecha_pedido', 'metodo_pago', 'items', 'productos'
        ]
        read_only_fields = ['total', 'fecha_pedido']

    def validate_productos(self, productos):
        if not productos:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        
        for item in productos:
            if not isinstance(item.get('producto_id'), int):
                raise serializers.ValidationError("producto_id debe ser un número entero")
            if not isinstance(item.get('cantidad', 1), int):
                raise serializers.ValidationError("cantidad debe ser un número entero")
            
            try:
                producto = Producto.objects.get(
                    id=item['producto_id'],
                    activo=True
                )
                if producto.stock < item.get('cantidad', 1):
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                    )
            except Producto.DoesNotExist:
                raise serializers.ValidationError(
                    f"El producto con ID {item['producto_id']} no existe o no está disponible"
                )
        
        return productos

    def create(self, validated_data):
        productos_data = validated_data.pop('productos')
        total_pedido = Decimal('0')

        with transaction.atomic():
            # Crear el pedido
            pedido = Pedido.objects.create(**validated_data)

            try:
                for item in productos_data:
                    producto_id = item['producto_id']
                    cantidad = item.get('cantidad', 1)

                    # Obtener el producto con bloqueo
                    producto = Producto.objects.select_for_update().get(
                        id=producto_id,
                        activo=True
                    )

                    # Validar stock nuevamente dentro de la transacción
                    if producto.stock < cantidad:
                        raise serializers.ValidationError(
                            f"Stock insuficiente para {producto.nombre}"
                        )

                    # Crear relación pedido-producto
                    precio_unitario = producto.precio_con_descuento
                    PedidoProducto.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario
                    )

                    # Actualizar stock
                    producto.stock -= cantidad
                    producto.save()

                    # Actualizar total
                    total_pedido += precio_unitario * Decimal(str(cantidad))

                # Guardar el total del pedido
                pedido.total = total_pedido
                pedido.save()

                return pedido

            except Exception as e:
                raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        # Usar el serializador detallado para la respuesta
        from .pedido_detalle_admin_serializers import PedidoDetalleAdminSerializer
        return PedidoDetalleAdminSerializer(instance, context=self.context).data