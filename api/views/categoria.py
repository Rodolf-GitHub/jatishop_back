from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Categoria, Subcategoria
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
    permission_classes = [IsNegocioOwnerOrReadOnly]

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
    permission_classes = [IsNegocioOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcategoriaDetalleSerializer
        return SubcategoriaSerializer