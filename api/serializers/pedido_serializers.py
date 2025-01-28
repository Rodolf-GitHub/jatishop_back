from rest_framework import serializers
from ..models import Pedido, PedidoProducto, Producto
from .producto_serializers import ProductoSerializer

class PedidoProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_precio = serializers.DecimalField(
        source='producto.precio',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = PedidoProducto
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_precio',
            'cantidad', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['precio_unitario', 'subtotal']

class PedidoSerializer(serializers.ModelSerializer):
    items = PedidoProductoSerializer(many=True, read_only=True)
    negocio_nombre = serializers.CharField(source='negocio.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'nombre_cliente', 'email_cliente', 'telefono_cliente',
            'direccion_entrega', 'negocio', 'negocio_nombre', 'items',
            'fecha_pedido', 'estado', 'estado_display', 'metodo_pago',
            'metodo_pago_display', 'nota_comprador', 'nota_vendedor', 'total', 'updated_at'
        ]
        read_only_fields = ['fecha_pedido', 'total', 'updated_at']

    def create(self, validated_data):
        items_data = self.context.get('items', [])
        pedido = Pedido.objects.create(**validated_data)

        for item_data in items_data:
            producto = item_data['producto']
            cantidad = item_data['cantidad']
            
            # Verificar que el producto pertenece al negocio del pedido
            if producto.subcategoria.categoria.negocio != pedido.negocio:
                raise serializers.ValidationError(
                    f"El producto {producto.nombre} no pertenece al negocio seleccionado"
                )

            PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad
            )

        pedido.calcular_total()
        return pedido

class PedidoDetalleSerializer(PedidoSerializer):
    items = PedidoProductoSerializer(many=True, read_only=True)
    
    class Meta(PedidoSerializer.Meta):
        fields = PedidoSerializer.Meta.fields + ['items']