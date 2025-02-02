from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from django.db.models import Q
from ...models import Pedido, NegocioUser, PedidoProducto
from ...serializers.admin_serializers.pedido_admin_serilizers import (
    PedidoAdminSerializer, 
    
)

@extend_schema_view(
    list=extend_schema(
        tags=['pedidos-admin'],
        description='Listar pedidos del negocio',
        responses={
            200: PedidoAdminSerializer(many=True),
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
        request=PedidoAdminSerializer,
        responses={
            201: PedidoAdminSerializer,
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
            200: PedidoAdminSerializer,
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
            200: PedidoAdminSerializer,
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
    permission_classes = [IsAuthenticated]
    serializer_class = PedidoAdminSerializer
    
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
        
        # Obtener pedidos que contengan productos de categorías del negocio
        return Pedido.objects.filter(
            items__producto__subcategoria__categoria__negocio=negocio
        ).prefetch_related(
            'items',
            'items__producto'
        ).distinct().order_by('-fecha_pedido')
    
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
            raise serializer.ValidationError(
                "No tienes un negocio asociado"
            )
        serializer.save(negocio=negocio)