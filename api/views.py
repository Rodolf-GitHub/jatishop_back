from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import InfoNegocio, Categoria, Subcategoria, Producto
from .serializers import (
    InfoNegocioSerializer, NegocioDetalleSerializer,
    CategoriaSerializer, CategoriaDetalleSerializer,
    SubcategoriaSerializer, SubcategoriaDetalleSerializer,
    ProductoSerializer
)
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .ubicaciones_cuba import PROVINCIAS, get_municipios as get_municipios_cuba

class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class InfoNegocioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InfoNegocioSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = InfoNegocio.objects.filter(activo=True)

        # Filtros de ubicación
        provincia = self.request.query_params.get('provincia')
        municipio = self.request.query_params.get('municipio')
        
        if provincia:
            queryset = queryset.filter(provincia=provincia)
            if municipio:
                queryset = queryset.filter(municipio=municipio)

        # Mantener búsqueda existente
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )

        return queryset

    def get_object(self):
        """
        Sobreescribimos get_object para usar negocio_slug de la URL
        """
        queryset = self.get_queryset()
        negocio_slug = self.kwargs.get('negocio_slug')
        if negocio_slug is None:
            return super().get_object()
        
        obj = get_object_or_404(queryset, slug=negocio_slug)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NegocioDetalleSerializer
        return InfoNegocioSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            negocios = serializer.data
            # Agregar información de ubicación explícita
            for negocio in negocios:
                obj = queryset.get(id=negocio['id'])
                negocio['ubicacion'] = {
                    'provincia': obj.provincia,
                    'municipio': obj.municipio
                }
            return self.get_paginated_response(negocios)

        serializer = self.get_serializer(queryset, many=True)
        negocios = serializer.data
        for negocio in negocios:
            obj = queryset.get(id=negocio['id'])
            negocio['ubicacion'] = {
                'provincia': obj.provincia,
                'municipio': obj.municipio
            }
        return Response(negocios)

class BaseNegocioViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        negocio_slug = self.kwargs.get('slug')
        
        if self.queryset.model == Categoria:
            return qs.filter(negocio__slug=negocio_slug)
        elif self.queryset.model == Subcategoria:
            return qs.filter(categoria__negocio__slug=negocio_slug)
        elif self.queryset.model == Producto:
            return qs.filter(subcategoria__categoria__negocio__slug=negocio_slug)
        return qs

class CategoriaViewSet(BaseNegocioViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoriaDetalleSerializer
        return CategoriaSerializer

    @action(detail=True, methods=['get'])
    def detalles(self, request, slug, pk=None):
        """Obtener todos los productos y subcategorías de una categoría"""
        categoria = self.get_object()
        subcategoria_id = request.query_params.get('subcategoria', None)
        search_query = request.query_params.get('search', '').strip()
        
        # Obtener subcategorías
        subcategorias = categoria.subcategorias.all()
        
        # Obtener productos
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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcategoriaDetalleSerializer
        return SubcategoriaSerializer

class ProductoViewSet(BaseNegocioViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    pagination_class = ProductPagination

    def list(self, request, *args, **kwargs):
        """Obtener todos los productos de una tienda"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def destacados(self, request, slug):
        """Obtener productos destacados del negocio"""
        productos = self.get_queryset()
        
        nuevos = productos.order_by('-created_at')[:5]
        ofertas = productos.filter(descuento__gt=0).order_by('-descuento')[:5]
        economicos = productos.order_by('precio')[:5]
        ultimas_unidades = productos.filter(stock__gt=0, stock__lte=5)[:5]

        return Response({
            'nuevos': ProductoSerializer(nuevos, many=True).data,
            'ofertas': ProductoSerializer(ofertas, many=True).data,
            'economicos': ProductoSerializer(economicos, many=True).data,
            'ultimas_unidades': ProductoSerializer(ultimas_unidades, many=True).data
        })

    @action(detail=False, methods=['get'])
    def por_categoria(self, request, slug):
        """Obtener productos por categoría"""
        categoria_id = request.query_params.get('categoria_id')
        if not categoria_id:
            return Response(
                {'error': 'Se requiere el parámetro categoria_id'}, 
                status=400
            )

        productos = self.get_queryset().filter(
            subcategoria__categoria_id=categoria_id
        )
        
        # Aplicar filtros adicionales si existen
        search = request.query_params.get('search', '').strip()
        if search:
            productos = productos.filter(nombre__icontains=search)

        # Ordenamiento
        orden = request.query_params.get('orden', '')
        if orden == 'precio_asc':
            productos = productos.order_by('precio')
        elif orden == 'precio_desc':
            productos = productos.order_by('-precio')
        elif orden == 'nuevos':
            productos = productos.order_by('-created_at')
        
        return Response(ProductoSerializer(productos, many=True).data)

    @action(detail=False, methods=['get'])
    def por_subcategoria(self, request, slug):
        """Obtener productos por subcategoría"""
        subcategoria_id = request.query_params.get('subcategoria_id')
        if not subcategoria_id:
            return Response(
                {'error': 'Se requiere el parámetro subcategoria_id'}, 
                status=400
            )

        productos = self.get_queryset().filter(
            subcategoria_id=subcategoria_id
        )
        
        # Aplicar filtros adicionales si existen
        search = request.query_params.get('search', '').strip()
        if search:
            productos = productos.filter(nombre__icontains=search)

        # Ordenamiento
        orden = request.query_params.get('orden', '')
        if orden == 'precio_asc':
            productos = productos.order_by('precio')
        elif orden == 'precio_desc':
            productos = productos.order_by('-precio')
        elif orden == 'nuevos':
            productos = productos.order_by('-created_at')
        
        return Response(ProductoSerializer(productos, many=True).data)

    def marketplace_list(self, request):
        """Lista todos los productos activos de todas las tiendas"""
        productos = Producto.objects.filter(
            activo=True,
            negocio__activo=True
        ).select_related('negocio')
        
        # Crear una respuesta que incluya el producto y su tienda
        response_data = []
        for producto in productos:
            producto_data = ProductoSerializer(producto).data
            producto_data['tienda'] = {
                'id': producto.subcategoria.categoria.negocio.id,
                'nombre': producto.subcategoria.categoria.negocio.nombre,
                'slug': producto.subcategoria.categoria.negocio.slug
            }
            response_data.append(producto_data)
            
        return Response(response_data)

class MarketplaceProductoViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               GenericViewSet):
    """
    ViewSet para listar productos en el marketplace.
    Solo permite operaciones de lectura (list y retrieve).
    """
    serializer_class = ProductoSerializer
    pagination_class = ProductPagination
    
    def get_queryset(self):
        queryset = Producto.objects.filter(
            activo=True,
            subcategoria__categoria__negocio__activo=True
        ).select_related(
            'subcategoria__categoria__negocio'
        ).order_by('-created_at')

        # Filtros de ubicación
        provincia = self.request.query_params.get('provincia')
        municipio = self.request.query_params.get('municipio')
        
        if provincia:
            queryset = queryset.filter(
                subcategoria__categoria__negocio__provincia=provincia
            )
            if municipio:
                queryset = queryset.filter(
                    subcategoria__categoria__negocio__municipio=municipio
                )

        # Mantener filtros existentes
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(nombre__icontains=search)

        categoria_id = self.request.query_params.get('categoria_id')
        if categoria_id:
            queryset = queryset.filter(subcategoria__categoria_id=categoria_id)

        subcategoria_id = self.request.query_params.get('subcategoria_id')
        if subcategoria_id:
            queryset = queryset.filter(subcategoria_id=subcategoria_id)

        # Ordenamiento
        orden = self.request.query_params.get('orden', '')
        if orden == 'precio_asc':
            queryset = queryset.order_by('precio')
        elif orden == 'precio_desc':
            queryset = queryset.order_by('-precio')
        elif orden == 'nuevos':
            queryset = queryset.order_by('-created_at')

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            productos = self.get_serializer(page, many=True).data
            
            # Agregar información de la tienda a cada producto
            for producto in productos:
                negocio = queryset.get(id=producto['id']).subcategoria.categoria.negocio
                producto['tienda'] = {
                    'id': negocio.id,
                    'nombre': negocio.nombre,
                    'slug': negocio.slug,
                    'provincia': negocio.provincia,
                    'municipio': negocio.municipio
                }
            return self.get_paginated_response(productos)

        productos = self.get_serializer(queryset, many=True).data
        for producto in productos:
            negocio = queryset.get(id=producto['id']).subcategoria.categoria.negocio
            producto['tienda'] = {
                'id': negocio.id,
                'nombre': negocio.nombre,
                'slug': negocio.slug,
                'provincia': negocio.provincia,
                'municipio': negocio.municipio
            }
        return Response(productos)

def home_view(request):
    return render(request, 'api/home.html')

@api_view(['GET'])
def get_provincias(request):
    """
    Retorna la lista de todas las provincias de Cuba.
    """
    return Response(PROVINCIAS)

@api_view(['GET'])
def get_municipios(request, provincia):
    """
    Retorna la lista de municipios de una provincia específica.
    """
    municipios = get_municipios_cuba(provincia)
    if not municipios:
        return Response(
            {'error': f'No se encontraron municipios para la provincia {provincia}'}, 
            status=404
        )
    return Response(municipios)