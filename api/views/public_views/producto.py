from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import (
    Producto, 
    InfoNegocio,
    Subcategoria,
    Categoria
)
from ..serializers import ProductoSerializer
from .base import BaseNegocioViewSet
from ..pagination import ProductPagination
from ..permissions import IsNegocioOwnerOrReadOnly
import logging

logger = logging.getLogger(__name__)

class ProductoViewSet(BaseNegocioViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    pagination_class = ProductPagination
    permission_classes = [IsNegocioOwnerOrReadOnly]

    def perform_create(self, serializer):
        negocio = self.get_negocio()
        # La validación de permisos ya la hace IsNegocioOwnerOrReadOnly
        serializer.save()

    # Los métodos perform_update y perform_destroy ya no necesitan 
    # validación adicional porque la hace IsNegocioOwnerOrReadOnly

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'por_subcategoria', 'por_categoria']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], url_path='categoria')
    def por_categoria(self, request, *args, **kwargs):
        try:
            # Obtener y validar categoria_id
            categoria_id = request.query_params.get('categoria_id')
            if not categoria_id:
                return Response(
                    {'error': 'Se requiere categoria_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que la categoría existe
            categoria = get_object_or_404(Categoria, id=categoria_id)
            
            # Obtener productos
            productos = Producto.objects.filter(
                subcategoria__categoria=categoria,
                activo=True
            ).select_related(
                'subcategoria',
                'subcategoria__categoria'
            )
            
            # Serializar y retornar
            serializer = ProductoSerializer(productos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Categoria.DoesNotExist:
            return Response(
                {'error': f'No existe la categoría con id {categoria_id}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error en por_categoria: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='subcategoria')
    def por_subcategoria(self, request, *args, **kwargs):
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
            logger.error(f"Error en por_subcategoria: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )