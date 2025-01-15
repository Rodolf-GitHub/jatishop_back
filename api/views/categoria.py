from rest_framework import permissions
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

class CategoriaViewSet(BaseNegocioViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    
    def get_permissions(self):
        """
        Permitir acceso público a list, retrieve y detalles
        """
        if self.action in ['list', 'retrieve', 'detalles']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsNegocioOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoriaDetalleSerializer
        return CategoriaSerializer

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

class SubcategoriaViewSet(BaseNegocioViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    
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