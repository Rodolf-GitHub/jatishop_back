from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import obtain_auth_token
# Importar las vistas directamente desde sus módulos
from .views.negocio import InfoNegocioViewSet
from .views.producto import ProductoViewSet
from .views.categoria import CategoriaViewSet, SubcategoriaViewSet
from .views.marketplace import MarketplaceProductoViewSet
from .views.ubicacion import get_provincias, get_municipios
from .views.auth import CustomAuthToken, logout, UserAuthViewSet

# Vista home simple
@api_view(['GET'])
def home_view(request):
    return Response({
        'message': 'Bienvenido a la API de JatiShop'
    })

# Router para el marketplace
marketplace_router = DefaultRouter()
marketplace_router.register(
    r'negocios', 
    InfoNegocioViewSet,  # Usar el mismo ViewSet que ya tiene los permisos configurados
    basename='marketplace-negocios'
)
marketplace_router.register(
    r'productos', 
    MarketplaceProductoViewSet, 
    basename='marketplace-productos'
)

@api_view(['GET'])
def api_root(request):
    return Response({
        'marketplace': {
            'descripcion': 'Endpoints del marketplace general',
            'url': f'{request.build_absolute_uri()}marketplace/'
        },
        'tiendas': {
            'descripcion': 'Endpoints específicos de tiendas',
            'ejemplo': f'{request.build_absolute_uri()}tienda/jatishop/'
        }
    })

urlpatterns = [
    # Vista principal
    path('', home_view, name='home'),
    
    # Vista raíz de la API
    path('api/', api_root, name='api-root'),

    # URLs de ubicaciones
    path('ubicaciones/provincias/', get_provincias, name='provincias'),
    path('ubicaciones/municipios/<str:provincia>/', get_municipios, name='municipios'),

    # URLs del marketplace
    path('marketplace/', include(marketplace_router.urls)),

    # URLs específicas de cada tienda
    path('tienda/<slug:slug>/', include([
        path('', InfoNegocioViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })),
        path('productos/', ProductoViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })),
        path('productos/<int:pk>/', ProductoViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })),
        path('categorias/', CategoriaViewSet.as_view({
            'get': 'list'
        })),
        path('categorias/<int:pk>/', CategoriaViewSet.as_view({
            'get': 'retrieve'
        })),
        path('categorias/<int:pk>/detalles/', CategoriaViewSet.as_view({
            'get': 'detalles'
        })),
        path('subcategorias/', SubcategoriaViewSet.as_view({
            'get': 'list'
        })),
        path('subcategorias/<int:pk>/', SubcategoriaViewSet.as_view({
            'get': 'retrieve'
        })),
        path('productos/destacados/', ProductoViewSet.as_view({
            'get': 'destacados'
        })),
        path('productos/categoria/', ProductoViewSet.as_view({
            'get': 'por_categoria'
        })),
        path('productos/subcategoria/', ProductoViewSet.as_view({
            'get': 'por_subcategoria'
        })),
    ])),
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    path('auth/logout/', logout, name='api_token_logout'),
    path('auth/register/', UserAuthViewSet.as_view({'post': 'create'}), name='user_register'),
]