from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view
from ...models import Producto, NegocioUser
from ...serializers import ProductoSerializer

@extend_schema_view(
    my_products=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar productos de mi negocio',
        methods=['GET', 'POST'],
        request=ProductoSerializer,
        responses={
            200: ProductoSerializer(many=True),
            201: ProductoSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    manage_product=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar un producto específico',
        methods=['PUT', 'PATCH', 'DELETE'],
        request=ProductoSerializer,
        responses={
            200: ProductoSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
)
class AdminProductoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Obtener productos del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        productos = Producto.objects.filter(
            subcategoria__categoria__negocio=negocio
        ).select_related(
            'subcategoria',
            'subcategoria__categoria'
        )
        
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_product(self, request):
        """Crear un nuevo producto para el negocio"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            subcategoria = serializer.validated_data['subcategoria']
            if subcategoria.categoria.negocio != negocio:
                return Response(
                    {'error': 'La subcategoría no pertenece a tu negocio'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch'])
    def update_product(self, request, pk=None):
        """Actualizar un producto específico"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            producto = Producto.objects.get(
                pk=pk,
                subcategoria__categoria__negocio=negocio
            )
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductoSerializer(
            producto,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            if 'subcategoria' in serializer.validated_data:
                subcategoria = serializer.validated_data['subcategoria']
                if subcategoria.categoria.negocio != negocio:
                    return Response(
                        {'error': 'La subcategoría no pertenece a tu negocio'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_product(self, request, pk=None):
        """Eliminar un producto específico"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            producto = Producto.objects.get(
                pk=pk,
                subcategoria__categoria__negocio=negocio
            )
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        producto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)