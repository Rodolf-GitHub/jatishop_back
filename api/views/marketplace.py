from rest_framework import viewsets, permissions
from ..models import Producto
from ..serializers import ProductoSerializer

class MarketplaceProductoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    
    def get_permissions(self):
        """
        Permitir acceso público a list y retrieve
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True)
        
        # Mantener los filtros existentes
        negocio_slug = self.request.query_params.get('negocio', None)
        if negocio_slug:
            queryset = queryset.filter(
                subcategoria__categoria__negocio__slug=negocio_slug
            )

        categoria_id = self.request.query_params.get('categoria', None)
        if categoria_id:
            queryset = queryset.filter(subcategoria__categoria_id=categoria_id)

        subcategoria_id = self.request.query_params.get('subcategoria', None)
        if subcategoria_id:
            queryset = queryset.filter(subcategoria_id=subcategoria_id)

        return queryset