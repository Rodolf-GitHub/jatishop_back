from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ...models import Pedido
from ...serializers import PedidoSerializer, PedidoDetalleSerializer

class PedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet público para consultar pedidos por teléfono
    """
    serializer_class = PedidoSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Pedido.objects.none()  # Por defecto no muestra nada
    
    @action(detail=False, methods=['get'])
    def consultar(self, request):
        telefono = request.query_params.get('telefono', None)
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