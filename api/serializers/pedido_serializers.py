from rest_framework import serializers
from ..models import Pedido, PedidoProducto, Producto
from decimal import Decimal

class PedidoProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = PedidoProducto
        fields = ['producto_id', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']

class PedidoSerializer(serializers.ModelSerializer):
    productos = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'nombre_cliente', 'email_cliente', 'telefono_cliente',
            'direccion_entrega', 'productos', 'nota_comprador', 'total'
        ]
        read_only_fields = ['total']

    def validate_productos(self, productos):
        if not productos:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        return productos

    def create(self, validated_data):
        productos_data = validated_data.pop('productos')
        pedido = Pedido.objects.create(**validated_data)
        total_pedido = Decimal('0')

        try:
            # Procesar productos
            for item in productos_data:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad', 1)

                try:
                    producto = Producto.objects.get(id=producto_id, activo=True)
                except Producto.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Producto {producto_id} no encontrado o no disponible"
                    )

                # Validar stock
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

            # Guardar total
            pedido.total = total_pedido
            pedido.save()

            return pedido

        except Exception as e:
            # Si algo falla, eliminar el pedido y revertir cambios
            if 'pedido' in locals():
                pedido.delete()
            raise serializers.ValidationError(str(e))

class PedidoDetalleSerializer(PedidoSerializer):
    items = PedidoProductoSerializer(source='pedidoproducto_set', many=True, read_only=True)
    
    class Meta(PedidoSerializer.Meta):
        fields = PedidoSerializer.Meta.fields + ['items', 'fecha_pedido', 'estado']