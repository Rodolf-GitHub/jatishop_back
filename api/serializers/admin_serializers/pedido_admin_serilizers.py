from rest_framework import serializers
from ...models import Pedido, PedidoProducto, Producto
from decimal import Decimal

class PedidoProductoAdminSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = PedidoProducto
        fields = [
            'id', 'producto_id', 'producto_nombre', 
            'cantidad', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['precio_unitario', 'subtotal']

class PedidoAdminSerializer(serializers.ModelSerializer):
    items = PedidoProductoAdminSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'nombre_cliente', 'email_cliente', 'telefono_cliente',
            'direccion_entrega', 'nota_comprador', 'total', 'estado',
            'fecha_pedido', 'metodo_pago', 'items'
        ]
        read_only_fields = ['total', 'fecha_pedido']

    def validate_productos(self, productos):
        if not productos:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        
        negocio = self.context.get('negocio')
        if not negocio:
            raise serializers.ValidationError("Negocio no encontrado")
        
        for item in productos:
            producto_id = item.get('producto_id')
            try:
                producto = Producto.objects.get(
                    id=producto_id,
                    subcategoria__categoria__negocio=negocio
                )
            except Producto.DoesNotExist:
                raise serializers.ValidationError(
                    f"El producto {producto_id} no pertenece a tu negocio"
                )
        
        return productos

    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        pedido = Pedido.objects.create(**validated_data)
        total_pedido = Decimal('0')

        try:
            for item in productos_data:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad', 1)

                producto = Producto.objects.select_for_update().get(
                    id=producto_id,
                    subcategoria__categoria__negocio=self.context['negocio']
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

            pedido.total = total_pedido
            pedido.save()

            return pedido

        except Exception as e:
            if 'pedido' in locals():
                pedido.delete()
            raise serializers.ValidationError(str(e))