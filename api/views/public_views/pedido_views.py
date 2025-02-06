from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from ...models import Pedido
from ...serializers import PedidoSerializer, PedidoDetalleSerializer

@extend_schema_view(
    list=extend_schema(
        tags=['pedidos'],
        description='Listar pedidos del usuario autenticado',
        responses={
            200: PedidoDetalleSerializer(many=True)
        }
    ),
    retrieve=extend_schema(
        tags=['pedidos'],
        description='Obtener detalle de un pedido del usuario',
        responses={
            200: PedidoDetalleSerializer,
            404: OpenApiResponse(
                description="Pedido no encontrado o no pertenece al usuario",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            )
        }
    ),
    cancelar=extend_schema(
        tags=['pedidos'],
        description='Cancelar un pedido pendiente',
        responses={
            200: OpenApiResponse(
                description="Pedido cancelado exitosamente",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description="El pedido no puede ser cancelado",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            )
        }
    )
)
class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pedidos del usuario autenticado
    """
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']  # Solo permitir GET y POST
    
    def get_queryset(self):
        return Pedido.objects.filter(
            email_cliente=self.request.user.email
        ).order_by('-fecha_pedido')
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return PedidoDetalleSerializer
        return PedidoSerializer

    def create(self, request):
        data = request.data.copy()
        data['email_cliente'] = request.user.email
        
        serializer = self.get_serializer(data=data)
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

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        try:
            pedido = self.get_object()
            
            # Verificar si el pedido está pendiente
            if pedido.estado != 'pendiente':
                return Response(
                    {'error': 'Solo se pueden cancelar pedidos pendientes'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cancelar el pedido
            pedido.estado = 'cancelado'
            pedido.save()
            
            return Response(
                {'message': 'Pedido cancelado exitosamente'},
                status=status.HTTP_200_OK
            )
            
        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context