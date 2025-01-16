from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Categoria, Subcategoria, Producto, InfoNegocio
from ..serializers import (
    CategoriaSerializer, CategoriaDetalleSerializer,
    SubcategoriaSerializer, SubcategoriaDetalleSerializer,
    ProductoSerializer
)
from .base import BaseNegocioViewSet
from ..permissions import IsNegocioOwnerOrReadOnly
import logging

logger = logging.getLogger(__name__)

class CategoriaViewSet(BaseNegocioViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsNegocioOwnerOrReadOnly]
    
    def get_permissions(self):
        """
        Permitir acceso público a list, retrieve y detalles
        """
        if self.action in ['list', 'retrieve', 'detalles', 'productos_subcategoria']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsNegocioOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoriaDetalleSerializer
        return CategoriaSerializer

    def get_queryset(self):
        negocio_slug = self.kwargs.get('negocio_slug')
        if not negocio_slug:
            return self.queryset.none()
        return self.queryset.filter(negocio__slug=negocio_slug)

    def perform_create(self, serializer):
        negocio_slug = self.kwargs.get('negocio_slug')
        negocio = get_object_or_404(InfoNegocio, slug=negocio_slug)
        serializer.save(negocio=negocio)

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
            subcategoria_id = request.query_params.get('subcategoria_id')
            if not subcategoria_id:
                return Response(
                    {'error': 'Se requiere subcategoria_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
            
            productos = Producto.objects.filter(
                subcategoria=subcategoria,
                activo=True
            ).select_related(
                'subcategoria',
                'subcategoria__categoria'
            )
            
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

class SubcategoriaViewSet(BaseNegocioViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    permission_classes = [IsNegocioOwnerOrReadOnly]
    
    def get_permissions(self):
        """
        Permitir acceso público a list y retrieve
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsNegocioOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcategoriaDetalleSerializer
        return SubcategoriaSerializer

    def get_queryset(self):
        negocio_slug = self.kwargs.get('negocio_slug')
        if not negocio_slug:
            return self.queryset.none()
        return self.queryset.filter(categoria__negocio__slug=negocio_slug)

    def perform_create(self, serializer):
        categoria = serializer.validated_data['categoria']
        if categoria.negocio.slug != self.kwargs.get('negocio_slug'):
            raise ValidationError('La categoría no pertenece a este negocio')
        serializer.save()