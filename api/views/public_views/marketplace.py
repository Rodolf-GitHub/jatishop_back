from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view
from ...models.producto_models import Producto
from ...serializers.producto_serializers import ProductoSerializer

class ProductoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema_view(
    list=extend_schema(
        tags=['marketplace'],
        description='Listar todos los productos del marketplace',
        parameters=[
            {'name': 'provincia', 'type': str, 'description': 'Filtrar por provincia'},
            {'name': 'municipio', 'type': str, 'description': 'Filtrar por municipio'},
            {'name': 'categoria', 'type': int, 'description': 'Filtrar por categoría'},
            {'name': 'subcategoria', 'type': int, 'description': 'Filtrar por subcategoría'},
            {'name': 'search', 'type': str, 'description': 'Buscar por nombre de producto'},
        ]
    ),
    retrieve=extend_schema(
        tags=['marketplace'],
        description='Obtener detalles de un producto específico'
    )
)
class MarketplaceProductoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer
    pagination_class = ProductoPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Solo filtramos por activo en las vistas públicas del marketplace
        queryset = Producto.objects.filter(
            activo=True,
            subcategoria__categoria__negocio__activo=True  # Filtramos negocios activos
        )
        
        # Búsqueda por nombre
        search_query = self.request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(nombre__icontains=search_query)
        
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

        # Filtros de provincia y municipio
        provincia = self.request.query_params.get('provincia', None)
        if provincia:
            queryset = queryset.filter(
                subcategoria__categoria__negocio__provincia__iexact=provincia
            )

        municipio = self.request.query_params.get('municipio', None)
        if municipio:
            queryset = queryset.filter(
                subcategoria__categoria__negocio__municipio__iexact=municipio
            )

        return queryset.select_related(
            'subcategoria',
            'subcategoria__categoria',
            'subcategoria__categoria__negocio'
        ).order_by('-id')