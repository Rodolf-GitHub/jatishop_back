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
    ViewSet público para gestionar pedidos
    """
    serializer_class = PedidoSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # Para consultas públicas, solo permitimos buscar por teléfono
        telefono = self.request.query_params.get('telefono')
        if telefono:
            return Pedido.objects.filter(telefono_cliente=telefono)
        return Pedido.objects.none()
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            pedido = serializer.save()
            return Response(
                PedidoDetalleSerializer(pedido).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
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