from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Categoria, Subcategoria, Producto
from ..serializers import (
    CategoriaSerializer, CategoriaDetalleSerializer,
    SubcategoriaSerializer, SubcategoriaDetalleSerializer,
    ProductoSerializer
)
from .base import BaseNegocioViewSet
from ..permissions import IsNegocioOwnerOrReadOnly
from django.shortcuts import get_object_or_404
import logging
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(tags=['categorias'], description='Listar categorías'),
    retrieve=extend_schema(tags=['categorias'], description='Obtener detalles de una categoría')
)
class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get'])
    def detalles(self, request, slug, pk=None):
        categoria = self.get_object()
        subcategoria_id = request.query_params.get('subcategoria', None)
        search_query = request.query_params.get('search', '').strip()
        
        subcategorias = categoria.subcategorias.all()
        productos = Producto.objects.filter(subcategoria__categoria=categoria)
        
        if subcategoria_id:
            productos = productos.filter(subcategoria_id=subcategoria_id)
        
        if search_query:
            productos = productos.filter(nombre__icontains=search_query)
        
        return Response({
            'categoria': CategoriaSerializer(categoria).data,
            'subcategorias': SubcategoriaSerializer(subcategorias, many=True).data,
            'productos': ProductoSerializer(productos, many=True).data
        })

    @action(detail=True, methods=['get'], url_path='productos/subcategoria')
    def productos_subcategoria(self, request, slug=None):
        try:
            # Obtener y validar subcategoria_id
            subcategoria_id = request.query_params.get('subcategoria_id')
            if not subcategoria_id:
                return Response(
                    {'error': 'Se requiere subcategoria_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que la subcategoría existe
            subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
            
            # Obtener productos
            productos = Producto.objects.filter(
                subcategoria=subcategoria,
                activo=True
            ).select_related(
                'subcategoria',
                'subcategoria__categoria'
            )
            
            # Serializar y retornar
            serializer = ProductoSerializer(productos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Subcategoria.DoesNotExist:
            return Response(
                {'error': f'No existe la subcategoría con id {subcategoria_id}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error en productos_subcategoria: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    list=extend_schema(tags=['categorias'], description='Listar subcategorías'),
    retrieve=extend_schema(tags=['categorias'], description='Obtener detalles de una subcategoría')
)
class SubcategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcategoriaDetalleSerializer
        return SubcategoriaSerializer