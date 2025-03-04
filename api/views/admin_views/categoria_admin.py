from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from ...models import Categoria, NegocioUser, Subcategoria
from ...serializers import CategoriaSerializer, SubcategoriaSerializer, CategoriaDetalleSerializer

@extend_schema_view(
    my_categories=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar categorías de mi negocio',
        methods=['GET', 'POST'],
        request=CategoriaSerializer,
        responses={
            200: CategoriaSerializer(many=True),
            201: CategoriaSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    manage_category=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar una categoría específica',
        methods=['PUT', 'PATCH', 'DELETE'],
        request=CategoriaSerializer,
        responses={
            200: CategoriaSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    subcategories=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar subcategorías de una categoría',
        methods=['GET', 'POST', 'PUT'],
        request=SubcategoriaSerializer,
        responses={
            200: SubcategoriaSerializer(many=True),
            201: SubcategoriaSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    ),
    manage_subcategory=extend_schema(
        tags=['mi-negocio'],
        description='Gestionar una subcategoría específica',
        methods=['PUT', 'PATCH', 'DELETE'],
        request=SubcategoriaSerializer,
        responses={
            200: SubcategoriaSerializer,
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
)
class AdminCategoriaViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_negocio(self, user):
        try:
            # No filtramos por activo para admin
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None

    @extend_schema(
        tags=['mi-negocio'],
        description='Gestionar categorías del negocio',
        methods=['GET', 'POST'],
        request=CategoriaSerializer,
        responses={
            200: CategoriaSerializer(many=True),
            201: CategoriaSerializer,
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
        },
        examples=[
            OpenApiExample(
                'Ejemplo de creación',
                value={
                    'nombre': 'Electrónica',
                    'descripcion': 'Productos electrónicos',
                    'imagen': 'archivo_imagen.jpg'
                }
            )
        ]
    )
    @action(detail=False, methods=['get', 'post'])
    def my_categories(self, request):
        """Obtener y crear categorías del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            categorias = Categoria.objects.filter(
                negocio=negocio
            ).prefetch_related('subcategorias')
            serializer = CategoriaDetalleSerializer(categorias, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CategoriaSerializer(data=request.data)
            if serializer.is_valid():
                categoria = serializer.save(negocio=negocio)
                return Response(
                    CategoriaDetalleSerializer(categoria).data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch', 'delete'])
    def manage_category(self, request, pk=None):
        """Gestionar una categoría específica"""
        negocio_user = NegocioUser.objects.get(user=request.user)

        try:
            categoria = Categoria.objects.get(pk=pk, negocio=negocio_user.negocio)
        except Categoria.DoesNotExist:
            return Response(
                {'error': 'Categoría no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method in ['PUT', 'PATCH']:
            serializer = CategoriaSerializer(
                categoria, 
                data=request.data, 
                partial=request.method=='PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            categoria.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post', 'put'])
    def subcategories(self, request, pk=None):
        """Gestionar subcategorías de una categoría"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            categoria = Categoria.objects.get(pk=pk, negocio=negocio)
        except Categoria.DoesNotExist:
            return Response(
                {'error': 'Categoría no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            subcategorias = Subcategoria.objects.filter(categoria=categoria)
            serializer = SubcategoriaSerializer(subcategorias, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            # Crear un nuevo diccionario con los datos del request
            data = request.data.copy()
            # Añadir el ID de la categoría
            data['categoria'] = categoria.id
            
            serializer = SubcategoriaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'PUT':
            subcategoria = Subcategoria.objects.get(pk=request.data.get('id'), categoria=categoria)
            serializer = SubcategoriaSerializer(subcategoria, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch', 'delete'], url_path='subcategories/(?P<subcategoria_pk>[^/.]+)')
    def manage_subcategory(self, request, pk=None, subcategoria_pk=None):
        """Gestionar una subcategoría específica"""
        negocio_user = NegocioUser.objects.get(user=request.user)

        try:
            categoria = Categoria.objects.get(pk=pk, negocio=negocio_user.negocio)
            subcategoria = Subcategoria.objects.get(pk=subcategoria_pk, categoria=categoria)
        except (Categoria.DoesNotExist, Subcategoria.DoesNotExist):
            return Response(
                {'error': 'Categoría o subcategoría no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method in ['PUT', 'PATCH']:
            data = request.data.copy()
            data['categoria'] = categoria.id
            serializer = SubcategoriaSerializer(
                subcategoria,
                data=data,
                partial=request.method=='PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            subcategoria.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)