from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from ...models import Pedido, NegocioUser
from ...serializers import PedidoSerializer, PedidoDetalleSerializer

@extend_schema_view(
    list=extend_schema(
        tags=['pedidos-admin'],
        description='Listar pedidos del negocio',
        responses={
            200: PedidoDetalleSerializer(many=True),
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    create=extend_schema(
        tags=['pedidos-admin'],
        description='Crear un nuevo pedido',
        request=PedidoSerializer,
        responses={
            201: PedidoSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    retrieve=extend_schema(
        tags=['pedidos-admin'],
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
    ),
    actualizar_estado=extend_schema(
        tags=['pedidos-admin'],
        description='Actualizar el estado de un pedido',
        request={
            'type': 'object',
            'properties': {
                'estado': {
                    'type': 'string',
                    'enum': ['pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado']
                }
            }
        },
        responses={
            200: PedidoDetalleSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Ejemplo de actualización',
                value={
                    'estado': 'confirmado'
                }
            )
        ]
    )
)
class AdminPedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que los administradores gestionen los pedidos de su negocio
    """
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None
    
    def get_queryset(self):
        negocio = self.get_negocio(self.request.user)
        if not negocio:
            return Pedido.objects.none()
        return Pedido.objects.filter(negocio=negocio)
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return PedidoDetalleSerializer
        return PedidoSerializer

    @action(detail=True, methods=['patch'])
    def actualizar_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Debe proporcionar un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if nuevo_estado not in dict(Pedido.ESTADO_CHOICES):
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        pedido.estado = nuevo_estado
        pedido.save()
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

    def perform_create(self, serializer):
        negocio = self.get_negocio(self.request.user)
        if not negocio:
            raise serializers.ValidationError(
                "No tienes un negocio asociado"
            )
        serializer.save(negocio=negocio)