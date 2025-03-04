from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from ...models import InfoNegocio, NegocioUser, TiendaTema, Categoria, Subcategoria, Producto
from ...serializers import InfoNegocioSerializer, TiendaTemaSerializer

@extend_schema_view(
    create_business=extend_schema(
        tags=['mi-negocio'],
        description='Crear un nuevo negocio',
        request=InfoNegocioSerializer,
        responses={
            201: InfoNegocioSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    my_business=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar mi negocio',
        methods=['GET', 'PUT', 'PATCH', 'DELETE'],
        request=InfoNegocioSerializer,
        responses={
            200: InfoNegocioSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    update_theme=extend_schema(
        tags=['mi-negocio'],
        description='Actualizar el tema de mi negocio',
        request=TiendaTemaSerializer,
        responses={
            200: TiendaTemaSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
)
class AdminNegocioViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None

    @extend_schema(
        tags=['mi-negocio'],
        description='Crear un nuevo negocio para el usuario autenticado',
        request=InfoNegocioSerializer,
        responses={
            201: InfoNegocioSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Ejemplo de solicitud',
                value={
                    'nombre': 'Mi Tienda',
                    'descripcion': 'Descripción de mi tienda',
                    'telefono': '+53 55555555',
                    'direccion': 'Dirección de mi tienda',
                    'provincia': 'La Habana',
                    'municipio': 'Plaza',
                }
            )
        ]
    )
    @action(detail=False, methods=['post'])
    def create_business(self, request):
        """Crear un nuevo negocio para el usuario autenticado"""
        if self.get_negocio(request.user):
            return Response(
                {'error': 'Ya tienes un negocio asociado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InfoNegocioSerializer(data=request.data)
        if serializer.is_valid():
            negocio = serializer.save()
            NegocioUser.objects.create(
                user=request.user,
                negocio=negocio,
                es_propietario=True
            )
            # Crear tema por defecto
            TiendaTema.objects.create(negocio=negocio)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['mi-negocio'],
        description='Gestionar información del negocio del usuario autenticado',
        methods=['GET', 'PUT', 'PATCH', 'DELETE'],
        request=InfoNegocioSerializer,
        responses={
            200: InfoNegocioSerializer,
            404: {
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
                    'nombre': 'Nuevo nombre de tienda',
                    'descripcion': 'Nueva descripción',
                    'telefono': '+53 55555555',
                }
            )
        ]
    )
    @action(detail=False, methods=['get', 'put', 'patch', 'delete'])
    def my_business(self, request):
        """Gestionar información del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = InfoNegocioSerializer(negocio)
            tema = TiendaTema.objects.get_or_create(negocio=negocio)[0]
            tema_serializer = TiendaTemaSerializer(tema)
            data = serializer.data
            data['tema'] = tema_serializer.data
            return Response(data)
            
        elif request.method in ['PUT', 'PATCH']:
            serializer = InfoNegocioSerializer(
                negocio, 
                data=request.data, 
                partial=request.method=='PATCH'
            )
            if serializer.is_valid():
                negocio = serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            negocio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'])
    def update_theme(self, request):
        """Actualizar el tema del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'},
                status=status.HTTP_404_NOT_FOUND
            )

        tema = TiendaTema.objects.get_or_create(negocio=negocio)[0]
        tema_serializer = TiendaTemaSerializer(
            tema,
            data=request.data,
            partial=True
        )
        if tema_serializer.is_valid():
            tema_serializer.save()
            return Response(tema_serializer.data)
        return Response(tema_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def get_resumen(self, request):
        """Obtener resumen de los recursos del usuario"""
        try:
            # Obtener el negocio del usuario
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            
            if not negocio_user:
                return Response({
                    'negocio': False,
                    'categoria': False,
                    'subcategoria': False,
                    'producto': False
                })

            negocio = negocio_user.negocio

            # Verificar si tiene categorías
            tiene_categorias = Categoria.objects.filter(negocio=negocio).exists()
            
            # Verificar si tiene subcategorías
            tiene_subcategorias = Subcategoria.objects.filter(
                categoria__negocio=negocio
            ).exists()
            
            # Verificar si tiene productos
            tiene_productos = Producto.objects.filter(
                subcategoria__categoria__negocio=negocio
            ).exists()

            return Response({
                'negocio': True,
                'categoria': tiene_categorias,
                'subcategoria': tiene_subcategorias,
                'producto': tiene_productos
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )