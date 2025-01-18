from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from ...models import Categoria, NegocioUser
from ...serializers import CategoriaSerializer

class AdminCategoriaViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
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
        """Gestionar categorías del negocio"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            categorias = Categoria.objects.filter(negocio=negocio)
            serializer = CategoriaSerializer(categorias, many=True)
            return Response(serializer.data)
            
        elif request.method == 'POST':
            serializer = CategoriaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(negocio=negocio)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch', 'delete'])
    def manage_category(self, request, pk=None):
        """Gestionar una categoría específica"""
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