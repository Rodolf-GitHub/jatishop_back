from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from ...models import Pedido, Producto, PedidoProducto
from ...serializers import PedidoSerializer, PedidoDetalleSerializer
from decimal import Decimal

@extend_schema_view(
    consultar=extend_schema(
        tags=['pedidos'],
        description='Consultar pedidos por número de teléfono',
        parameters=[
            OpenApiParameter(
                name='telefono',
                description='Número de teléfono del cliente',
                required=True,
                type=str
            )
        ],
        responses={
            200: PedidoDetalleSerializer(many=True),
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    list=extend_schema(
        tags=['pedidos'],
        description='Listar pedidos (requiere teléfono)',
        responses={
            200: PedidoSerializer(many=True)
        }
    ),
    retrieve=extend_schema(
        tags=['pedidos'],
        description='Obtener detalle de un pedido',
        responses={
            200: PedidoDetalleSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
)
class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet público para consultar pedidos por teléfono
    """
    serializer_class = PedidoSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Pedido.objects.none()
    
    def create(self, request):
        # Validar datos básicos del pedido
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar productos
        productos_data = request.data.get('productos', [])
        if not productos_data:
            return Response(
                {'error': 'Debe incluir al menos un producto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Crear pedido
            pedido = serializer.save()
            total_pedido = Decimal('0.00')
            
            # Procesar cada producto
            for item in productos_data:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad', 1)
                
                try:
                    producto = Producto.objects.get(id=producto_id, activo=True)
                except Producto.DoesNotExist:
                    pedido.delete()
                    return Response(
                        {'error': f'Producto {producto_id} no encontrado o no disponible'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Validar stock
                if producto.stock < cantidad:
                    pedido.delete()
                    return Response(
                        {'error': f'Stock insuficiente para el producto {producto.nombre}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calcular precio con descuento si existe
                precio_unitario = producto.precio_con_descuento
                
                # Crear relación pedido-producto
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
            
            # Actualizar total del pedido
            pedido.total = total_pedido
            pedido.save()
            
            # Retornar detalles del pedido
            return Response(
                PedidoDetalleSerializer(pedido).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Si algo falla, eliminar el pedido
            if 'pedido' in locals():
                pedido.delete()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def consultar(self, request):
        telefono = request.query_params.get('telefono')
        if not telefono:
            return Response(
                {'error': 'Debe proporcionar un número de teléfono'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        pedidos = Pedido.objects.filter(
            telefono_cliente=telefono
        ).order_by('-fecha_pedido')
        
        if not pedidos.exists():
            return Response(
                {'error': 'No se encontraron pedidos con ese número de teléfono'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = PedidoDetalleSerializer(pedidos, many=True)
        return Response(serializer.data)